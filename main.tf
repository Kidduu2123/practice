resource "local_file" "filea" {
filename = "${path.module}/mydir1/filea1.txt"
content = var.filea
}

resource "local_file" "fileb" {
filename = "${path.module}/mydir2/fileb1.txt"
content = var.fileb
}
