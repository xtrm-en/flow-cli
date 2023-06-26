# Features

## `fart aliases`
Setup aliases .bashrc/.zshrc/.fishrc

## `fart check`
Norminette + GCC (max? flags)

## `fart config`
- Flags
- Norminette
- Makefile
- Libft

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

## `fart tester` or `fart tester generate c01 ex1`
```
check if c file is <CNameList>
strlen -> slkjebkjHEBfjhkwbef = 19
strlen_tester.c
```

## `fart watch`
Repliquer comportement `watch -n0 fart check` (en gros)

## `fart valgrind`
memcheck + leaks + flags
