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
sh 'terraform plan'
}
}
stage('Validate'){
steps{
sh 'terraform validate'
}
}
stage('Apply'){
steps{
sh 'terraform apply –auto-approve'
}
}
}
}
