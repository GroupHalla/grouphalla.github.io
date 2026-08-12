# grouphalla.github.io

Site oficial e registro global de emblemas visuais do Halla.

## Endpoints públicos

- `https://grouphalla.github.io/badges/v1/badges.json`
- `https://grouphalla.github.io/badges/v1/badges.json.sig`
- `https://grouphalla.github.io/badges/v1/icons/<id>.png`

O manifesto é assinado com Ed25519. Desktop e Mobile possuem a chave pública
oficial embutida e mantêm a última versão válida em cache. Emblemas são
estritamente visuais: nunca concedem permissões em servidores.

## Atribuir emblemas

Edite `badges/v1/badges.json` e associe a UID criptográfica do usuário:

```json
"users": {
  "UID_COMPLETA_DO_USUARIO": ["dev", "founder"]
}
```

Regras:

- no máximo 8 emblemas por UID;
- toda referência deve existir em `badges`;
- ícones devem ser PNG, ter no máximo 128 KiB e SHA-256 correto;
- a relação UID/emblema é pública e deve ser publicada com consentimento;
- nunca adicione a chave privada de assinatura ao repositório.

## Validar e assinar localmente

```bash
python3 tools/validate_badges.py
./tools/sign_badges.sh /caminho/seguro/Halla-Badges-Ed25519-Private.pem
```

No GitHub, o workflow de Pages valida e assina automaticamente o manifesto com
o secret `BADGES_SIGNING_PRIVATE_KEY_PEM` antes da publicação.

A chave pública oficial possui SHA-256:

```text
f08f74e7bfae2e1c04efd73d77c76eecbbb3c009f6792e25bd5a6ba856cee9fa
```
