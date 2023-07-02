# Features
#### `flow setup`
- [ ] aliases .bashrc/.zshrc/.fishrc
- [ ] jsp

#### `flow check`
- [x] norminette
- [ ] compiler
- [ ] foreign function access

##### `flow config`
- [x] Flags
- [x] Norminette
- [ ] Makefile
- [ ] Libft


- [ ] `flow compile [<name>]`
```
if makefile
->make <name of project(found in makefile)>
else
-> gcc + -Wall -Werror -Wextra *.c *.h
end
```

- [ ] `flow run`
```
if makefile
->make <name of project(found in makefile)>
else
-> gcc + -Wall -Werror -Wextra *.c *.h
end

-> ./a.out
->rm ./a.out
```

- [ ] `flow test` 
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

- [ ] `flow watch`
Repliquer comportement `watch -n0 flow check` (en gros)

- [x] `flow valgrind`
memcheck + leaks + flags
