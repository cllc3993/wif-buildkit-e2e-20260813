FROM alpine:3.22 AS source-snapshot
WORKDIR /app
COPY . .
RUN test -n "$(find /app -name 'gha-creds-*.json' -print -quit)"

FROM alpine:3.22
COPY lab/benign-canary.txt /canary
CMD ["cat", "/canary"]
