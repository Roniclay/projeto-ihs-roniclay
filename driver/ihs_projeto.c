#include <linux/module.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/uaccess.h>
#include <linux/string.h>

#define NOME_DRIVER "ihs_projeto"
#define NOME_DISPOSITIVO "ihs_projeto"
#define NOME_CLASSE "ihs"
#define TAMANHO_NOTA 5

static dev_t numero_dispositivo;
static struct cdev ihs_cdev;
static struct class *ihs_classe;

static char nota_atual[TAMANHO_NOTA + 1] = "00000";

static int validar_nota(const char *nota)
{
    int i;

    for (i = 0; i < TAMANHO_NOTA; i++) {
        if (nota[i] != '0' && nota[i] != '1') {
            return -EINVAL;
        }
    }

    return 0;
}


static ssize_t ihs_write(struct file *file, const char __user *user_buffer,
                         size_t count, loff_t *offset)
{
    char kernel_buffer[16];
    size_t bytes_to_copy;
    size_t tamanho_nota;
    int ret;

    if (count == 0) {
        return 0;
    }

    if (count >= sizeof(kernel_buffer)) {
        pr_warn("%s: entrada muito grande\n", NOME_DRIVER);
        return -EINVAL;
    }

    bytes_to_copy = count;

    if (copy_from_user(kernel_buffer, user_buffer, bytes_to_copy)) {
        pr_warn("%s: falha ao copiar dados do espaco do usuario\n", NOME_DRIVER);
        return -EFAULT;
    }

    kernel_buffer[bytes_to_copy] = '\0';

    
    tamanho_nota = strcspn(kernel_buffer, "\n\r");

    if (tamanho_nota != TAMANHO_NOTA) {
        pr_warn("%s: nota com tamanho invalido: %zu\n",
                NOME_DRIVER, tamanho_nota);
        return -EINVAL;
    }

    kernel_buffer[TAMANHO_NOTA] = '\0';

    ret = validar_nota(kernel_buffer);
    if (ret != 0) {
        pr_warn("%s: nota invalida: %s\n", NOME_DRIVER, kernel_buffer);
        return ret;
    }

    memcpy(nota_atual, kernel_buffer, TAMANHO_NOTA + 1);

    pr_info("%s: nota recebida: %s\n", NOME_DRIVER, nota_atual);

    return count;
}


static ssize_t ihs_read(struct file *file, char __user *user_buffer,
                        size_t count, loff_t *offset)
{
    char output_buffer[TAMANHO_NOTA + 2];
    int len;

    len = scnprintf(output_buffer, sizeof(output_buffer),
                    "%s\n", nota_atual);

    return simple_read_from_buffer(user_buffer, count, offset,
                                   output_buffer, len);
}


static const struct file_operations ihs_fops = {
    .owner = THIS_MODULE,
    .write = ihs_write,
    .read = ihs_read,
};

static int __init ihs_projeto_init(void)
{
    int ret;
    struct device *ihs_dispositivo;

    pr_info("%s: iniciando modulo\n", NOME_DRIVER);

    ret = alloc_chrdev_region(&numero_dispositivo, 0, 1, NOME_DISPOSITIVO);
    if (ret < 0) {
        pr_err("%s: erro ao alocar major/minor\n", NOME_DRIVER);
        return ret;
    }

   
    cdev_init(&ihs_cdev, &ihs_fops);
    ihs_cdev.owner = THIS_MODULE;

   
    ret = cdev_add(&ihs_cdev, numero_dispositivo, 1);
    if (ret < 0) {
        pr_err("%s: erro ao registrar cdev\n", NOME_DRIVER);
        unregister_chrdev_region(numero_dispositivo, 1);
        return ret;
    }

   
    ihs_classe = class_create(NOME_CLASSE);
    if (IS_ERR(ihs_classe)) {
        ret = PTR_ERR(ihs_classe);
        pr_err("%s: erro ao criar classe\n", NOME_DRIVER);

        cdev_del(&ihs_cdev);
        unregister_chrdev_region(numero_dispositivo, 1);

        return ret;
    }

   
    ihs_dispositivo = device_create(ihs_classe, NULL, numero_dispositivo,
                                    NULL, NOME_DISPOSITIVO);
    if (IS_ERR(ihs_dispositivo)) {
        ret = PTR_ERR(ihs_dispositivo);
        pr_err("%s: erro ao criar dispositivo\n", NOME_DRIVER);

        class_destroy(ihs_classe);
        cdev_del(&ihs_cdev);
        unregister_chrdev_region(numero_dispositivo, 1);

        return ret;
    }

    pr_info("%s: modulo carregado com sucesso\n", NOME_DRIVER);
    pr_info("%s: dispositivo criado em /dev/%s\n",
            NOME_DRIVER, NOME_DISPOSITIVO);
    pr_info("%s: major=%d minor=%d\n",
            NOME_DRIVER,
            MAJOR(numero_dispositivo),
            MINOR(numero_dispositivo));

    return 0;
}


static void __exit ihs_projeto_exit(void)
{
    device_destroy(ihs_classe, numero_dispositivo);
    class_destroy(ihs_classe);
    cdev_del(&ihs_cdev);
    unregister_chrdev_region(numero_dispositivo, 1);

    pr_info("%s: modulo removido com sucesso\n", NOME_DRIVER);
}

module_init(ihs_projeto_init);
module_exit(ihs_projeto_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Roniclay");
MODULE_DESCRIPTION("Driver projeto IHS");
MODULE_VERSION("0.2");