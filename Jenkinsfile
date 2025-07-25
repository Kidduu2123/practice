pipeline{
stages(‘Init'){
steps{
sh terraform init
}
}
stages(‘Plan’){
steps{
Sh terraform plan
}
}
stages(‘Validate’){
steps{
Sh terraform validate
}
}
stages(‘Apply’){
steps{
sh terraform apply –auto-approve
}
}
}
