**Settings**
Library     SimpleRemote    target_1

**Test Cases**
TestCase1
    ${result}=  multiply     a=${2}      b=${3}
    should be equal     ${result}   ${6}

TestCase2
    ${result}=  add     ${1}   ${2}
    should be equal     ${result}   ${3}
    ${result}=  multiply     a=${2}      b=${3}
    should be equal     ${result}   ${6}