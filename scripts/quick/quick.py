from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def generate_hello(packet_number: bytes, dcid: bytes, scid: bytes, payload: bytes) -> bytes:
    """
    Generate a QUIC Hello packet (Client or Server)

    :param packet_number: Packet number as bytes
    :param dcid: Destination Connection ID as bytes
    :param scid: Source Connection ID as bytes
    :param payload: The crypto payload to be sent in the QUIC packet
    :return: QUIC Hello packet as bytes
    """
    version = b'\xff\x00\x00\x1d'  # QUIC draft version prior to RFC 9000
    token_len = b'\x00'

    # Initial packet flags (0b1100_0000 for Initial packet, followed by 0b0000_0000 for fixed bits)
    packet_type_flags = b'\xc0'
    length = len(packet_number) + len(payload)  # Simplified, does not include variable length integers encoding

    # Assemble the packet
    quic_packet = bytearray(packet_type_flags)
    quic_packet += version
    quic_packet += len(dcid).to_bytes(1, byteorder='big') + dcid
    quic_packet += len(scid).to_bytes(1, byteorder='big') + scid
    quic_packet += token_len  # Token length is 0, so no token is appended
    quic_packet += length.to_bytes(2, byteorder='big')  # Simplified length calculation
    quic_packet += packet_number
    quic_packet += payload

    return bytes(quic_packet)


def decode_quic_packet(quic_packet: bytes):
    """
    Decode a QUIC packet and extract the packet number and payload.

    :param quic_packet: The QUIC packet as bytes
    :return: Packet number and payload as bytes
    """
    # Extract the packet number
    packet_number = quic_packet[6:14]

    # Extract the payload
    payload = quic_packet[14:]

    return packet_number, payload


def perform_ecdhe_and_derive_key(peer_public_key_bytes):
    """
    Perform ECDHE operation and derive the shared secret key.

    :param peer_public_key_bytes: The public key bytes of the peer (client/server).
    :return: Derived shared key.
    """
    # Generate your own private key for ECDHE
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())

    # Load the peer's public key
    peer_public_key = serialization.load_pem_public_key(peer_public_key_bytes, default_backend())

    # Compute the shared secret
    shared_secret = private_key.exchange(ec.ECDH(), peer_public_key)

    # Derive a shared key from the shared secret
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data',  # Placeholder for actual handshake context data
        backend=default_backend()
    ).derive(shared_secret)

    return derived_key


def derive_handshake_secrets(shared_secret):
    """
    Derive handshake traffic secrets from the shared secret and handshake hash,
    using proper info values according to TLS 1.3.

    :param shared_secret: The shared secret from the (EC)DHE operation.
    :return: A tuple of (client_handshake_secret, server_handshake_secret).
    """
    # Salt for HKDF-Extract is the handshake hash, providing handshake-specific context
    # TODO Left for @varshashaheen to implement
    salt = b'\x00' * 32  # Simplified, assuming SHA-256 hash length

    # Derive the pseudorandom key (prk) from the shared secret and salt
    prk = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=b'',  # Info is used in the expand phase, not extract
        backend=default_backend()
    )._extract(shared_secret)

    # Derive client_handshake_secret
    hkdf_expand_client = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,  # Not needed for the expand phase
        info=b'tls13 client handshake traffic secret',
        backend=default_backend()
    )
    client_handshake_secret = hkdf_expand_client.derive(prk)

    # Derive server_handshake_secret
    hkdf_expand_server = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,  # Not needed for the expand phase
        info=b'tls13 server handshake traffic secret',
        backend=default_backend()
    )
    server_handshake_secret = hkdf_expand_server.derive(prk)

    return client_handshake_secret, server_handshake_secret


def create_finished_message(secret, handshake_hash):
    """Create the 'Finished' message with HMAC."""
    h = hmac.HMAC(secret, hashes.SHA256(), backend=default_backend())
    h.update(handshake_hash)
    return h.finalize()


def create_quic_finished_packet(secret):
    """
    Creates a QUIC packet containing the Finished message.

    :param secret: The secret key used to create the HMAC for the Finished message.
    :return: A QUIC packet with the Finished message.
    """
    # Hash the handshake messages
    handshake_hash = b'\x00' * 32

    # Create the Finished message using the secret and the hash of handshake messages
    finished_message = create_finished_message(secret, handshake_hash)

    packet_type = b'\x02'  # Arbitrary type for Finished message
    payload_length = len(finished_message).to_bytes(2, 'big')  # Assuming 2 bytes for length
    quic_packet = packet_type + payload_length + finished_message

    return quic_packet
