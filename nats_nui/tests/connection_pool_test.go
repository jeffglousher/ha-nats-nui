package connection

import (
	"context"
	"errors"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

func TestHAConnectionEventsConcurrentCancellation(t *testing.T) {
	conn := &NatsConn{mockMode: true}
	defer conn.Close()
	var workers sync.WaitGroup
	for worker := 0; worker < 4; worker++ {
		workers.Add(1)
		go func() {
			defer workers.Done()
			for i := 0; i < 500; i++ {
				ctx, cancel := context.WithCancel(context.Background())
				ch := conn.ObserveConnectionEvents(ctx)
				conn.handleEvent(StatusConnected, nil)
				_, _ = conn.LastEvent()
				cancel()
				for range ch {
					// Wait for cancellation to close the subscription.
				}
			}
		}()
	}
	workers.Wait()
}

type haPoolConn struct{ closes atomic.Int32 }

func (c *haPoolConn) Close() { c.closes.Add(1) }

func TestHAConnPoolRetriesFailedRefresh(t *testing.T) {
	repo := NewMemConnRepo()
	_, _ = repo.Save(&Connection{Id: "test"})
	calls := 0
	pool := NewConnPool[*haPoolConn](repo, func(*Connection) (*haPoolConn, error) {
		calls++
		if calls == 2 {
			return nil, errors.New("temporary connection failure")
		}
		return &haPoolConn{}, nil
	})
	first, err := pool.Get("test")
	if err != nil {
		t.Fatal(err)
	}
	if err = pool.Refresh("test"); err == nil {
		t.Fatal("expected simulated refresh failure")
	}
	recovered, err := pool.Get("test")
	if err != nil {
		t.Fatal(err)
	}
	if recovered == first || recovered.closes.Load() != 0 || calls != 3 {
		t.Fatal("failed refresh returned a closed cached connection instead of retrying")
	}
	if first.closes.Load() != 1 {
		t.Fatal("replaced connection must be closed exactly once")
	}
}

func TestHAConnPoolPurgeWaitsForLock(t *testing.T) {
	pool := NewConnPool[*haPoolConn](NewMemConnRepo(), func(*Connection) (*haPoolConn, error) {
		return &haPoolConn{}, nil
	})
	pool.m.Lock()
	finished := make(chan struct{})
	go func() { pool.Purge(); close(finished) }()
	select {
	case <-finished:
		pool.m.Unlock()
		t.Fatal("Purge accessed the pool without acquiring its mutex")
	case <-time.After(100 * time.Millisecond):
		pool.m.Unlock()
	}
	select {
	case <-finished:
	case <-time.After(5 * time.Second):
		t.Fatal("Purge did not finish after the mutex was released")
	}
}

func TestHAConnPoolConcurrentPurgeAndRefresh(t *testing.T) {
	repo := NewMemConnRepo()
	_, _ = repo.Save(&Connection{Id: "test"})
	pool := NewConnPool[*haPoolConn](repo, func(*Connection) (*haPoolConn, error) {
		return &haPoolConn{}, nil
	})
	var workers sync.WaitGroup
	for worker := 0; worker < 4; worker++ {
		workers.Add(1)
		go func() {
			defer workers.Done()
			for i := 0; i < 1000; i++ {
				_ = pool.Refresh("test")
				pool.Purge()
				_, _ = pool.Get("test")
			}
		}()
	}
	workers.Wait()
}
