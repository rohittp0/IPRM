import os


def generate_server_hello_payload():
    # TLS handshake type for Server Hello
    handshake_type_server_hello = b'\x02'

    # Version for TLS 1.3
    tls_version = b'\x03\x03'  # TLS 1.2 version number for compatibility

    # Random bytes
    server_random = os.urandom(32)

    # Session ID (echoed back; in TLS 1.3, it's typically empty)
    session_id = b'\x00'

    # Cipher Suite selected (TLS_AES_128_GCM_SHA256)
    cipher_suite = b'\x13\x01'

    # Compression Method selected (null compression method)
    compression_method = b'\x00'

    # Constructing the Server Hello message
    server_hello = (
            handshake_type_server_hello +
            b'\x00\x00\x00' +  # Placeholder for length (3 bytes)
            tls_version +
            server_random +
            session_id +
            cipher_suite +
            compression_method
    )

    # Correcting the length field
    server_hello_length = len(server_hello) - 4  # Subtract the handshake type and length fields
    server_hello = (
            server_hello[:1] +
            server_hello_length.to_bytes(3, byteorder='big') +
            server_hello[4:]
    )

    # Encapsulating in a QUIC CRYPTO Frame (simplified representation)
    crypto_frame = (
            b'\x06' +  # Frame type for CRYPTO (simplified)
            b'\x00' +  # Start of the crypto stream
            len(server_hello).to_bytes(2, byteorder='big') +
            server_hello
    )

    return crypto_frame


def decode_server_hello_payload(server_hello_payload):
    # Extract the Server Random
    server_random = server_hello_payload[6:38]

    return server_random
