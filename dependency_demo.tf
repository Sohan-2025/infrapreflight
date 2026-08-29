resource "local_file" "config" {
  filename = "config.txt"
  content  = "database=production"
}

resource "local_file" "application" {
  filename = "application.txt"

  content = local_file.config.content
}

resource "local_file" "backup" {
  filename = "backup.txt"
  content  = "backup"

  depends_on = [
    local_file.application
  ]
}