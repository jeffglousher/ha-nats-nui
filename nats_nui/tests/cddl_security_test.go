package cddlschema

import (
 "os"
 "path/filepath"
 "testing"
)

func TestHAPathContainment(t *testing.T) {
 dir := t.TempDir()
 root := filepath.Join(dir, "schemas")
 if err := os.MkdirAll(filepath.Join(root, "nested"), 0700); err != nil { t.Fatal(err) }
 for _, file := range []string{filepath.Join(root,"nested","valid.cddl"),filepath.Join(dir,"outside.cddl")} {
  if err := os.WriteFile(file, []byte("sample = { name: tstr }"),0600); err != nil { t.Fatal(err) }
 }
 repo := &FileSystemCddlRepo{baseDir:root, l: &recordingLogger{}}
 if _,err := repo.GetById("nested/valid"); err != nil { t.Fatal(err) }
 if _,err := repo.GetById("../outside"); err == nil { t.Fatal("traversal allowed") }
 if err := os.Symlink(filepath.Join(dir,"outside.cddl"),filepath.Join(root,"linked.cddl")); err != nil { t.Fatal(err) }
 if _,err := repo.GetById("linked"); err == nil { t.Fatal("symlink escape allowed") }
 schemas,err := repo.All()
 if err != nil || len(schemas)!=1 { t.Fatalf("unexpected enumeration: %v %v",schemas,err) }
}
