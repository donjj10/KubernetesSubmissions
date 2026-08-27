# Log output app

Log Output and Ping-Pong share data through a PersistentVolumeClaim.

Deploy infrastructure with:

`kubectl apply -f infra/storage/`

Deploy the applications with:

`kubectl apply -f log_output/manifests/`

`kubectl apply -f ping_pong/manifests/`
