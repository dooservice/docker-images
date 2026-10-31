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
    "16.0" = "d44c567db80a01d38c1dc3ff20874c167e443163"
    "17.0" = "2213db622f3a7997bc0e9908ce0f608d39cb9fda"
    "18.0" = "43e1a106350b16da09952973997809edae1a1b06"
    "19.0" = "30fcc77afb728d3bcf90baabeeb880bd77438c2a"
    "20.0" = "60269b95f3279bc4a17bf9bbe8539d4f53f78734"
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
