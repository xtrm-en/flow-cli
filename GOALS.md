# Features
#### `fart setup`
- [ ] aliases .bashrc/.zshrc/.fishrc
- [ ] jsp

#### `fart check`
- [x] norminette
- [ ] compiler
- [ ] foreign function access

##### `fart config`
- [x] Flags
- [x] Norminette
- [ ] Makefile
- [ ] Libft


- [ ] `fart compile [<name>]`
```
if makefile
->make <name of project(found in makefile)>
else
-> gcc + -Wall -Werror -Wextra *.c *.h
end
```

- [ ] `fart run`
```
if makefile
->make <name of project(found in makefile)>
else
-> gcc + -Wall -Werror -Wextra *.c *.h
end

-> ./a.out
->rm ./a.out
```

- [ ] `fart test` 
```
reimpl_main.c

if (ft_strlen(CONDITION), strlen(EGAL))
    return 1;
```

```    
check if c file is [ListCFiles]
strlen -> slkjebkjHEBfjhkwbef = 19
strlen_tester.c
```

- [ ] `fart watch`
Repliquer comportement `watch -n0 fart check` (en gros)

- [x] `fart valgrind`
memcheck + leaks + flags
