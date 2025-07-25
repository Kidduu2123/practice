pipeline{
Stages(‘Init){
Steps{
sh terraform init
}
}
stages(‘Plan’){
steps{
Sh terraform plan
}
}
stages(‘Validate’){
Steps{
Sh terraform validate
}
}
Stages(‘Apply’){
Steps{
Sh terraform apply –auto-approve
}
}
