# Every image this repository builds, for `docker buildx bake`.
#
# Nothing is pushed unless asked: `make build` loads an image locally, and the build
# workflow adds `--push`. Each image gets two tags: the version, which moves with every
# build, and the version with the revision, which never moves once pushed.
#
#   docker buildx bake --load odoo-19-0
#   docker buildx bake --load operator-19-0
#   REVISION=20261031 ODOO_VERSIONS=18.0,19.0 docker buildx bake --push odoo operator

variable "REGISTRY" {
  default = "ghcr.io/dooservice"
}

# The build's revision: the UTC date, with -2, -3... when the day already has one.
variable "REVISION" {
  default = "local"
}

# The Odoo versions to build, comma-separated: the keys of [odoo] in the agent's platform.toml.
variable "ODOO_VERSIONS" {
  default = "16.0,17.0,18.0,19.0,20.0"
}

# The commit of this repository the images are built from.
variable "SOURCE_COMMIT" {
  default = ""
}

# The commit of dooservice/odoo-addons each Odoo image carries: a branch per version there,
# and here the exact commit, so a revision of an image always carries the same modules.
# A commit goes here only once its branch is pushed to dooservice/odoo-addons.
variable "ADDONS_COMMITS" {
  type = map(string)
  default = {
    "16.0" = "4514c57bd8b76219f2dd07815e9276e73752e686"
    "17.0" = "f4081dfd0b891a3bb747c1461eaa45b5909544f0"
    "18.0" = "a8f8ec7ca52104c346fcbb3b6365d0bf5ef7ea73"
    "19.0" = "5f2d4489736599133751f9c5a309c6e10a36fb6e"
    "20.0" = "c53251d19a30f00c5db499485202618eae06f6cf"
  }
}

# The official odoo image each version is built on, by digest: a revision is built from
# exactly these bytes, and a new digest arrives as a reviewed change (Renovate proposes it).
variable "ODOO_DIGESTS" {
  type = map(string)
  default = {
    "16.0" = "sha256:0f36a5002a200bb1649771c2cb9403ca5392d7ac4bb23f9ad500b339df3f5a3a"
    "17.0" = "sha256:8779f8157ddcc37b84014c94646073f46fd4ad776b7a5d95fc3b0dc73a24a8fa"
    "18.0" = "sha256:9668abacd894276ed009e8db7db1d1ffb8068af6982f76a3400ed0d68e40432d"
    "19.0" = "sha256:27f920e002c43a1af7022a68f3cc17db71a2f9f3348800cb050721ce54893e49"
    "20.0" = "sha256:a97a7665e2b9fd890e12785491a2c91d779f800bcbc30873dada1c8748b28f1c"
  }
}

function "versions" {
  params = []
  result = [for version in split(",", ODOO_VERSIONS) : trimspace(version)]
}

function "tags" {
  params = [image, version]
  result = [
    "${REGISTRY}/${image}:${version}",
    "${REGISTRY}/${image}:${version == "latest" ? REVISION : "${version}-${REVISION}"}",
  ]
}

function "labels" {
  params = [title, description, version]
  result = {
    "org.opencontainers.image.title"       = title
    "org.opencontainers.image.description" = description
    "org.opencontainers.image.version"     = version
    "org.opencontainers.image.revision"    = SOURCE_COMMIT
    "org.opencontainers.image.source"      = "https://github.com/dooservice/docker-images"
    "org.opencontainers.image.url"         = "https://dooservice.sh"
    "org.opencontainers.image.vendor"      = "Dooservice"
    "org.opencontainers.image.licenses"    = "AGPL-3.0-only"
  }
}

group "default" {
  targets = ["odoo", "operator", "postgres", "status"]
}

target "common" {
  platforms = ["linux/amd64"]
}

target "odoo" {
  inherits = ["common"]
  name     = "odoo-${replace(version, ".", "-")}"
  matrix = {
    version = versions()
  }
  context = "odoo"
  args = {
    ODOO_VERSION  = version
    ODOO_DIGEST   = ODOO_DIGESTS[version]
    ADDONS_COMMIT = ADDONS_COMMITS[version]
  }
  labels = merge(labels("dooservice-odoo", "Odoo ${version} as Dooservice runs it", "${version}-${REVISION}"), {
    "sh.dooservice.addons-commit" = ADDONS_COMMITS[version]
  })
  tags = tags("dooservice-odoo", version)
}

# The console is built on the Odoo image of the same build, never on a tag that may have moved.
target "operator" {
  inherits = ["common"]
  name     = "operator-${replace(version, ".", "-")}"
  matrix = {
    version = versions()
  }
  context = "operator"
  contexts = {
    dooservice-odoo = "target:odoo-${replace(version, ".", "-")}"
  }
  args = {
    ODOO_VERSION = version
  }
  labels = labels("dooservice-operator", "The console of an Odoo ${version} environment", "${version}-${REVISION}")
  tags   = tags("dooservice-operator", version)
}

target "postgres" {
  inherits = ["common"]
  context  = "postgres"
  labels   = labels("dooservice-postgres", "PostgreSQL 16 with pgvector", "16-${REVISION}")
  tags     = tags("dooservice-postgres", "16")
}

target "status" {
  inherits = ["common"]
  context  = "status"
  labels   = labels("dooservice-status", "The page a server shows while an environment is down", REVISION)
  tags     = tags("dooservice-status", "latest")
}
