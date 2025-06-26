FROM rust:1.88.0-alpine3.22 as build


RUN apk add --no-cache build-base musl-dev protoc protobuf-dev libressl-dev curl

WORKDIR /usr/service
COPY Cargo.toml Cargo.lock ./

# Build and cache deps
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo fetch
RUN cargo build --release --bin milky-blog-service
RUN rm src/main.rs

# Copy actual files and build
COPY migrations ./migrations
COPY src ./src
COPY proto ./proto
COPY build.rs .

RUN touch src/main.rs
RUN cargo build --release --bin milky-blog-service


FROM alpine:3.20


RUN apk add --no-cache openssl

WORKDIR /usr/local/bin

COPY --from=build /usr/service/target/release/milky-blog-service .

CMD ["milky-blog-service"]