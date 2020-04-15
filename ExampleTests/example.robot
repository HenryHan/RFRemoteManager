**Test Cases**
TestCase1
    Import Library     SimpleRemote    10.91.44.163     WITH NAME       client
    client.add     ${1}   ${1}
    client.multiply     a=${2}     b=${3}