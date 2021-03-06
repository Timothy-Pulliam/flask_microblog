# self signed cert
verify_ssl_cert () {
  openssl pkey -in privateKey.key -pubout -outform pem | sha256sum
  openssl x509 -in certificate.crt -pubkey -noout -outform pem | sha256sum
  openssl req -in CSR.csr -pubkey -noout -outform pem | sha256sum
}

create_self_signed_ssl_cert () {
  # Creates an SSL cert and installs it on nginx
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt
}
