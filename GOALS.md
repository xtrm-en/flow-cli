# FEATURES

## `fart compile [<name>]`
```
if makefile
->make <name of project(found in makefile)>
else
-> gcc + -Wall -Werror -Wextra *.c *.h
end
```
## `fart run`
```
if makefile
->make <name of project(found in makefile)>
else
-> gcc + -Wall -Werror -Wextra *.c *.h
end

-> ./a.out
->rm ./a.out
```

## `fart tester or fart tester generate c01 ex1`
```
check if c file is <CNameList>
strlen -> slkjebkjHEBfjhkwbef = 19
strlen_tester.c
```

fart setup