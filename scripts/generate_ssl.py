import os
import sys
import datetime

def generate_self_signed_cert(output_dir='docker/nginx/certs', cert_name='library'):
    os.makedirs(output_dir, exist_ok=True)
    cert_path = os.path.join(output_dir, f"{cert_name}.crt")
    key_path = os.path.join(output_dir, f"{cert_name}.key")

    if os.path.exists(cert_path) and os.path.exists(key_path):
        print(f"[+] SSL certificate already exists at:\n    - {cert_path}\n    - {key_path}")
        return

    print(f"[*] Generating self-signed SSL certificate for local demo in '{output_dir}'...")

    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import ipaddress

        # Generate private key
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # Subject & Issuer
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "VN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Hanoi"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Hanoi"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "DevOps University"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Library System"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.DNSName("library.local"),
                    x509.DNSName("web"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                ]),
                critical=False,
            )
            .sign(key, hashes.SHA256())
        )

        # Write private key
        with open(key_path, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))

        # Write certificate
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        print(f"[+] Successfully generated self-signed certificate:")
        print(f"    - Certificate: {cert_path}")
        print(f"    - Private Key: {key_path}")

    except ImportError:
        # Fallback to openssl CLI if cryptography is not available
        import subprocess
        git_openssl = r"C:\Program Files\Git\usr\bin\openssl.exe"
        openssl_bin = git_openssl if os.path.exists(git_openssl) else "openssl"

        cmd = [
            openssl_bin, "req", "-x509", "-newkey", "rsa:2048",
            "-keyout", key_path,
            "-out", cert_path,
            "-days", "365",
            "-nodes",
            "-subj", "/C=VN/ST=Hanoi/L=Hanoi/O=DevOps/CN=localhost"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[+] Successfully generated certificate using openssl CLI:")
            print(f"    - Certificate: {cert_path}")
            print(f"    - Private Key: {key_path}")
        else:
            print(f"[-] Failed to generate certificate: {res.stderr}")
            sys.exit(1)

if __name__ == '__main__':
    generate_self_signed_cert()
