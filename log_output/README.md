# Log output app

The application runs as two containers in a single Pod:

- `log-generator` writes timestamp + random string to a shared file.
- `log-reader` reads the shared file and serves it over HTTP.

Run with `kubectl apply -f manifests/`

View generator logs with `kubectl logs -f deployment/log-output -c log-generator`

View reader logs with `kubectl logs -f deployment/log-output -c log-reader`
