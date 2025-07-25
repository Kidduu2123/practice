resource "local_file" "filea" {
filename = "${path.module}/mydir/filea.txt"
content = var.filea
}

resource "local_file" "fileb" {
filename = "${path.module}/mydir/fileb.txt"
content = var.fileb
}
