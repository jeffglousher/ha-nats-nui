package nui

import (
    "errors"
    "io"
    "log/slog"
    "net/http/httptest"
    "strings"
    "testing"
    "github.com/nats-nui/nui/internal/connection"
)

type unavailablePool struct{}
func (unavailablePool) Get(string) (*connection.NatsConn, error) { return nil, errors.New("test broker unavailable") }
func (unavailablePool) Refresh(string) error { return nil }
func (unavailablePool) Purge() {}

func TestHABucketUnavailableReturnsErrorWithoutPanic(t *testing.T) {
    app := NewServer("0", &Nui{ConnPool: unavailablePool{}}, slog.New(slog.NewTextHandler(io.Discard, nil)), false)
    for _, route := range []struct{ method, path string }{
        {"GET", "/kv"}, {"POST", "/kv"}, {"GET", "/kv/bucket"},
        {"POST", "/kv/bucket"}, {"DELETE", "/kv/bucket"},
        {"GET", "/kv/bucket/key"}, {"GET", "/kv/bucket/key/check"},
        {"POST", "/kv/bucket/key/check"}, {"POST", "/kv/bucket/purge_deleted"},
    } {
        t.Run(route.method+route.path, func(t *testing.T) {
            req := httptest.NewRequest(route.method, "/api/connection/missing"+route.path, strings.NewReader("{}"))
            req.Header.Set("Content-Type", "application/json")
            response, err := app.Test(req)
            if err != nil { t.Fatal(err) }
            defer response.Body.Close()
            if response.StatusCode != 422 { t.Fatalf("status = %d", response.StatusCode) }
        })
    }
}
