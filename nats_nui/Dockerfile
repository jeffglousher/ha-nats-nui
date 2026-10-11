FROM golang:1.27.2-alpine@sha256:f92b6ef800e499660581efdabdf25d9d817a9d124eaf900924f0504e7e27e12d AS backend
RUN apk upgrade --no-cache && apk add --no-cache git nodejs npm gcc musl-dev
ENV GOTOOLCHAIN=go1.27.2
WORKDIR /src
# Development integration: current CBOR/CDDL plus latest SUBJECTS/watch.
RUN git init . && git remote add origin https://github.com/jeffglousher/nui.git \
    && git fetch --depth 1 origin 46bca9281a3254a3ce66deb56c44faffc205991a \
    && git checkout --detach FETCH_HEAD
COPY dependencies/go.mod dependencies/go.sum /src/
COPY dependencies/package.json dependencies/package-lock.json /src/frontend/
COPY patches/bucket-wire-format.patch /tmp/bucket-wire-format.patch
RUN git apply --check /tmp/bucket-wire-format.patch && git apply /tmp/bucket-wire-format.patch
COPY tests/buckets.test.ts /src/frontend/src/api/buckets.test.ts
COPY schemas/agent-board.cddl /src/agent-board.cddl
COPY tests/board-cbor.test.ts /src/frontend/src/utils/cbor/ha-contract.test.ts
RUN cd frontend && npm ci --ignore-scripts --no-audit --no-fund && npm exec -- vitest run && npm run build
# No non-ingress listener: the backend is reachable only inside this container.
RUN grep -F 'return a.Listen(":" + a.Port)' internal/nui/server.go \
    && sed -i 's/return a.Listen(":" + a.Port)/return a.Listen("127.0.0.1:" + a.Port)/' internal/nui/server.go
COPY patches/service-logs.patch /tmp/service-logs.patch
RUN git apply --check /tmp/service-logs.patch && git apply /tmp/service-logs.patch
COPY patches/schema-containment.patch /tmp/schema-containment.patch
RUN git apply --check /tmp/schema-containment.patch && git apply /tmp/schema-containment.patch
COPY patches/cddl-containment.patch /tmp/cddl-containment.patch
RUN git apply --check /tmp/cddl-containment.patch && git apply /tmp/cddl-containment.patch
COPY patches/connection-pool.patch /tmp/connection-pool.patch
RUN git apply --check /tmp/connection-pool.patch && git apply /tmp/connection-pool.patch
COPY patches/connection-events.patch /tmp/connection-events.patch
RUN git apply --check /tmp/connection-events.patch && git apply /tmp/connection-events.patch
COPY patches/bucket-recovery.patch /tmp/bucket-recovery.patch
RUN git apply --check /tmp/bucket-recovery.patch && git apply /tmp/bucket-recovery.patch
COPY tests/bucket_errors_test.go /src/internal/nui/ha_bucket_errors_test.go
RUN go test ./internal/nui -run TestHABucketUnavailable -count=1
COPY tests/connection_pool_test.go /src/internal/connection/ha_pool_test.go
RUN CGO_ENABLED=1 go test -race ./internal/connection -count=1 -timeout=2m
COPY tests/schema_security_test.go /src/internal/protoschema/ha_security_test.go
RUN go test ./internal/protoschema -run TestHAPathContainment -count=1
COPY tests/cddl_security_test.go /src/internal/cddlschema/ha_security_test.go
RUN go test ./internal/cddlschema -count=1
RUN CGO_ENABLED=0 go build -ldflags '-X main.Version=0.9.3-ha-cbor-subjects.2+46bca928' -o /nui-web ./cmd/server/main.go
RUN go run golang.org/x/vuln/cmd/govulncheck@v1.8.0 -mode=binary /nui-web

FROM ghcr.io/nats-nui/nui:0.9.3@sha256:331b3f34f8aa626f88e3aa3e35749196607a3a56d7fddc6fb642938dcd659c04 AS runtime
USER root
RUN apk upgrade --no-cache && apk add --no-cache nginx tini su-exec jq python3 && mkdir -p /run/nginx
ARG BUILD_VERSION
ARG BUILD_ARCH
LABEL io.hass.type="addon" io.hass.version="${BUILD_VERSION}" io.hass.arch="${BUILD_ARCH}"
COPY --from=backend /nui-web /cmd/nui-web
RUN rm -rf /frontend/dist && mkdir -p /frontend/dist
COPY --from=backend /src/frontend/dist /frontend/dist
COPY nginx.conf /etc/nginx/nginx.conf
COPY run.sh /run.sh
COPY provision.py /provision.py
COPY schemas/ /usr/share/nui/cddlschemas/
COPY ha-init.js /frontend/dist/ha-init.js
RUN grep -q '<head>' /frontend/dist/index.html \
    && sed -i 's|<head>|<head><script src="./ha-init.js"></script>|' /frontend/dist/index.html
RUN chmod 755 /run.sh && touch /run/nginx/console-admins.map && nginx -t
ENTRYPOINT ["/sbin/tini", "-g", "--", "/run.sh"]
CMD []

FROM runtime AS validation
RUN apk upgrade --no-cache && apk add --no-cache python3 nodejs
COPY tests/provision.py /provision-test.py
RUN python3 /provision-test.py
COPY tests/runtime.py /runtime-test.py
COPY tests/frontend.cjs /frontend/tests/frontend.cjs
COPY ha-init.js /frontend/ha-init.js
RUN node /frontend/tests/frontend.cjs && python3 /runtime-test.py

FROM runtime AS final
COPY --from=validation /test-passed /usr/share/addon-runtime-tests.txt
