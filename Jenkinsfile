pipeline{
  agent any
  stages{
stage('Init'){
steps{
sh 'terraform init'
}
}
stage('Plan'){
steps{
Sh 'terraform plan'
}
}
stage('Validate'){
steps{
Sh 'terraform validate'
}
}
stage('Apply'){
steps{
sh 'terraform apply –auto-approve'
}
}
}
}
