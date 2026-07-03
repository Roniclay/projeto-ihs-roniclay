#include <linux/module.h>
#include <linux/init.h>

#define NOME_DRIVE "ihs_projeto"

static int __init ihs_projeto_init(void)
{
  pr_info("%s: Modulo foi carregado!\n", NOME_DRIVE);
  return 0;
}

static void __exit ihs_projeto_exit(void)
{
  pr_info("%s: Modulo foi removido!\n", NOME_DRIVE);
}

module_init(ihs_projeto_init);
module_exit(ihs_projeto_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Roniclay");
MODULE_DESCRIPTION("Driver inicial do projeto IHS para luva/simulador MAMIP");
MODULE_VERSION("0.1");