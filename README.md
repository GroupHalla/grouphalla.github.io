# grouphalla.github.io

Official GroupHalla website — publishes the **signed badge registry** used by
Halla clients (Desktop and Mobile).

- Landing page: `index.html` (English by default, with EN / PT / ES switcher)
- Badge manifest: [`badges/v1/badges.json`](badges/v1/badges.json) (Ed25519
  signed, `badges.json.sig`)
- Signing public key: `badges/v1/signing-public-key.pem`

Badges are strictly visual and grant no permissions on servers. The manifest
is consumed by the clients at runtime; badge names and descriptions are shown
exactly as published in the signed registry.
