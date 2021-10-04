load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
http_archive(
    name = "rules_python",
    url = "https://github.com/bazelbuild/rules_python/releases/download/0.4.0/rules_python-0.4.0.tar.gz",
    sha256 = "954aa89b491be4a083304a2cb838019c8b8c3720a7abb9c4cb81ac7a24230cea",
)

load("@rules_python//python:pip.bzl", "pip_install")
pip_install(
    name = "third_party",
    python_interpreter = "python3",
    requirements = "//third_party:requirements.txt",
)

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
http_archive(
    name = "io_bazel_rules_docker",
    sha256 = "1f4e59843b61981a96835dc4ac377ad4da9f8c334ebe5e0bb3f58f80c09735f4",
    strip_prefix = "rules_docker-0.19.0",
    urls = ["https://github.com/bazelbuild/rules_docker/releases/download/v0.19.0/rules_docker-v0.19.0.tar.gz"],
)

load(
    "@io_bazel_rules_docker//repositories:repositories.bzl",
    container_repositories = "repositories",
)
container_repositories()

load("@io_bazel_rules_docker//repositories:deps.bzl", container_deps = "deps")
container_deps()

load(
    "@io_bazel_rules_docker//python3:image.bzl",
    _py_image_repos = "repositories",
)
_py_image_repos()

load(
    "@io_bazel_rules_docker//container:container.bzl",
    "container_pull",
)

container_pull(
    name = "python3.8_image",
    registry = "index.docker.io",
    repository = "python",
    tag = "3.8",
)

http_archive(
    name = "rules_proto_grpc",
   sha256 = "4202a150910712d00d95f11e240ad6da4c92e542d3b9fbb5b3a3d60abba3de77",
    strip_prefix = "rules_proto_grpc-4.0.0",
    urls = ["https://github.com/rules-proto-grpc/rules_proto_grpc/archive/4.0.0.tar.gz"],
)

load("@rules_proto_grpc//:repositories.bzl", "rules_proto_grpc_toolchains", "rules_proto_grpc_repos")
rules_proto_grpc_toolchains()
rules_proto_grpc_repos()

load("@rules_proto//proto:repositories.bzl", "rules_proto_dependencies", "rules_proto_toolchains")
rules_proto_dependencies()
rules_proto_toolchains()

load("@rules_proto_grpc//python:repositories.bzl", rules_proto_grpc_python_repos = "python_repos")
rules_proto_grpc_python_repos()

load("@com_github_grpc_grpc//bazel:grpc_deps.bzl", "grpc_deps")
grpc_deps()

pip_install(
    name = "rules_proto_grpc_py3_deps",
    python_interpreter = "python3",
    requirements = "@rules_proto_grpc//python:requirements.txt",
)

http_archive(
    name = "io_bazel_rules_k8s",
    strip_prefix = "rules_k8s-0.5",
    urls = ["https://github.com/bazelbuild/rules_k8s/archive/v0.5.tar.gz"],
    sha256 = "773aa45f2421a66c8aa651b8cecb8ea51db91799a405bd7b913d77052ac7261a",
)

load("@io_bazel_rules_k8s//k8s:k8s.bzl", "k8s_repositories")
k8s_repositories()

load("@io_bazel_rules_k8s//k8s:k8s_go_deps.bzl", k8s_go_deps = "deps")
k8s_go_deps()

load("@io_bazel_rules_k8s//k8s:k8s.bzl", "k8s_defaults")
k8s_defaults(
    name = "k8s_deploy",
    cluster = "arcturus",
    namespace = "iu-lms",
    user = "deployer",
    context = "default",
)

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_file")
http_file(
    name = "grpc_health_check_bin",
    downloaded_file_path = "grpc_health_probe",
    urls = ["https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/v0.3.2/grpc_health_probe-linux-amd64"],
)
