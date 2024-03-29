import os


def generate_client_hello_payload():
    # TLS handshake type for Client Hello
    handshake_type_client_hello = b'\x01'

    # Version for TLS 1.3
    tls_version = b'\x03\x03'  # TLS 1.2 version number for compatibility

    # Random bytes
    client_random = os.urandom(32)

    # Session ID (empty for TLS 1.3)
    session_id = b'\x00'

    # Cipher Suites (only TLS_AES_128_GCM_SHA256 is supported)
    cipher_suites = b'\x13\x01'  # TLS_AES_128_GCM_SHA256
    cipher_suites_length = b'\x00\x02'  # Length in bytes

    # Compression Methods (null compression method only)
    compression_methods = b'\x00'
    compression_methods_length = b'\x01'

    # Constructing the Client Hello message
    client_hello = (
            handshake_type_client_hello +
            b'\x00\x00\x00' +  # Placeholder for length (3 bytes)
            tls_version +
            client_random +
            session_id +
            cipher_suites_length + cipher_suites +
            compression_methods_length + compression_methods +
            b'\x00\x00'  # Extensions length - since no extensions are supported, this is 0
    )

    # Correcting the length field
    client_hello_length = len(client_hello) - 4  # Subtract the handshake type and length fields
    client_hello = (
            client_hello[:1] +
            client_hello_length.to_bytes(3, byteorder='big') +
            client_hello[4:]
    )

    # Encapsulating in a QUIC CRYPTO Frame (simplified representation)
    crypto_frame = (
            b'\x06' +  # Assuming frame type for CRYPTO is 0x06 (simplified)
            b'\x00' +  # Assuming start of the crypto stream
            len(client_hello).to_bytes(2, byteorder='big') +
            client_hello
    )

    return crypto_frame


def decode_server_hello_payload(server_hello_payload):
    # Extract the Server Random
    server_random = server_hello_payload[6:38]

    return server_random
