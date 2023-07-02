{INCLUDES}
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

{TARGET_FUNCTION}

static int progress = 0;

void    fart_catchsig(int signal, siginfo_t *si, void *arg)
{
    printf("%d ERR (SIG: %d)\n", progress, signal);
    fflush(stdout);
	exit(-1);
}

void    fart_check(int works)
{
    if (works)
        printf("%d OK\n", progress);
    else
        printf("%d ERR\n", progress);
    fflush(stdout);
}

int main(int argc, char *argv[])
{
    // Setup segfault catching
    // from: https://stackoverflow.com/a/2436368
    struct sigaction sa;
	memset(&sa, 0, sizeof(struct sigaction));
    sigemptyset(&sa.sa_mask);
    sa.sa_sigaction = fart_catchsig;
    sa.sa_flags = SA_SIGINFO;
    sigaction(SIGSEGV, &sa, NULL);

    progress = 1;

    {STARTCHECK}
    fart_check({TEST_TARGET} == {TEST_SOURCE});
    progress++;
    {ENDCHECK}

    printf("DONE %d\n", progress);
    fflush(stdout);

    return 0;
}
