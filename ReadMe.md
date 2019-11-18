Scripts for building Debian/Ubuntu packages for building software
=================================================================

Scripts in this repo are [Unlicensed ![](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/).

Third-party components have own licenses.

**DISCLAIMER: BADGES BELOW DO NOT REFLECT THE STATE OF THE DEPENDENCIES IN THE CONTAINER**

The software in this repo builds some packages useful for building software.

Artifacts of CI builds can be used as a repo for apt.

```bash
export ARTIFACTS_PATH=https://kolanich-subgroups.gitlab.io/packages/build_tools
export KEY_FINGERPRINT=F7245DAA5F3C4ADF9C30435220486A680275B5E5
export REPO_NAME=build_tools_KOLANICH
curl -o $REPO_NAME.gpg $ARTIFACTS_PATH/public.gpg
apt-key add $REPO_NAME.gpg
eval `apt-config shell TRUSTED_KEYS_DIR Dir::Etc::TrustedParts/d`
export KEY_PATH=$TRUSTED_KEYS_DIR/$REPO_NAME.gpg
mv ./$REPO_NAME.gpg $KEY_PATH
echo deb [arch=amd64,signed-by=$KEY_PATH] $ARTIFACTS_PATH/repo $(lsb_release -sc) contrib >> /etc/apt/sources.list.d/$REPO_NAME.list
apt update
```

To install the packages, use `vanilla-` prefix:

```bash
apt-get -y install vanilla-cmake
```

Setting up an own repo
==================

1. generate a GPG private key (RSA 4096, signature only)

2. export it
```bash
gpg --no-default-keyring --keyring ./kr.gpg --export-secret-key $KEY_FINGERPRINT | base64 -w0 > ./private.gpg.b64
```
`-w0` is mandatory.

3. paste it into GitLab protected environment variable `GPG_KEY`




