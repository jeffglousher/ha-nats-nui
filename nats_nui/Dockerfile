FROM golang:1.27-alpine@sha256:cf6fca6641884b8433441b2b0652976f975e1d0fdd26d177eaaf8596087f3125 AS backend
RUN apk add --no-cache git nodejs npm
ENV GOTOOLCHAIN=go1.27.1
WORKDIR /src
RUN git init . && git remote add origin https://github.com/nats-nui/nui.git \
    && git fetch --depth 1 origin ba291a34430c0bdd0d2b45e070a153e62a45289c \
    && git checkout --detach FETCH_HEAD
COPY dependencies/go.mod dependencies/go.sum /src/
COPY dependencies/package.json dependencies/package-lock.json /src/frontend/
RUN cd frontend && npm ci --ignore-scripts --no-audit --no-fund && npm exec -- vitest run && npm run build
# No non-ingress listener: the backend is reachable only inside this container.
RUN grep -F 'return a.Listen(":" + a.Port)' internal/nui/server.go \
    && sed -i 's/return a.Listen(":" + a.Port)/return a.Listen("127.0.0.1:" + a.Port)/' internal/nui/server.go
COPY patches/service-logs.patch /tmp/service-logs.patch
RUN git apply --check /tmp/service-logs.patch && git apply /tmp/service-logs.patch
COPY patches/schema-containment.patch /tmp/schema-containment.patch
RUN git apply --check /tmp/schema-containment.patch && git apply /tmp/schema-containment.patch
COPY tests/schema_security_test.go /src/internal/protoschema/ha_security_test.go
RUN go test ./internal/protoschema -run TestHAPathContainment -count=1
RUN CGO_ENABLED=0 go build -ldflags '-X main.Version=0.9.3' -o /nui-web ./cmd/server/main.go
RUN go run golang.org/x/vuln/cmd/govulncheck@v1.8.0 -mode=binary /nui-web

FROM ghcr.io/nats-nui/nui:0.9.3@sha256:331b3f34f8aa626f88e3aa3e35749196607a3a56d7fddc6fb642938dcd659c04 AS runtime
USER root
RUN apk add --no-cache nginx tini su-exec jq && mkdir -p /run/nginx
ARG BUILD_VERSION
ARG BUILD_ARCH
LABEL io.hass.type="addon" io.hass.version="${BUILD_VERSION}" io.hass.arch="${BUILD_ARCH}"
COPY --from=backend /nui-web /cmd/nui-web
RUN rm -rf /frontend/dist && mkdir -p /frontend/dist
COPY --from=backend /src/frontend/dist /frontend/dist
COPY nginx.conf /etc/nginx/nginx.conf
COPY run.sh /run.sh
COPY ha-init.js /frontend/dist/ha-init.js
RUN grep -q '<head>' /frontend/dist/index.html \
    && sed -i 's|<head>|<head><script src="./ha-init.js"></script>|' /frontend/dist/index.html
RUN chmod 755 /run.sh && nginx -t
ENTRYPOINT ["/sbin/tini", "-g", "--", "/run.sh"]
CMD []

FROM runtime AS validation
RUN apk add --no-cache python3 nodejs
COPY tests/runtime.py /runtime-test.py
COPY tests/frontend.cjs /frontend/tests/frontend.cjs
COPY ha-init.js /frontend/ha-init.js
RUN node /frontend/tests/frontend.cjs && python3 /runtime-test.py

FROM runtime AS final
COPY --from=validation /test-passed /usr/share/addon-runtime-tests.txt
