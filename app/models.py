from django.db import models

# Ejemplo Create your models here.
class estadoMueble(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.descripcion
class disponiblidadMueble(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)
    def __str__(self):
        return self.descripcion
    
class categoriaMueble(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)
    def __str__(self):
        return self.descripcion

class mueble(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=50)
    foto = models.ImageField(
        upload_to= 'productos',
        null= True,
        blank= True,
    )
    precio = models.IntegerField()
    cantidad = models.IntegerField(default=0)
    estado = models.ForeignKey(
        estadoMueble,
        on_delete= models.CASCADE
    )
    disponiblidad = models.ForeignKey(
        disponiblidadMueble,
        on_delete= models.CASCADE
    )
    categoria_mueble = models.ForeignKey(
        categoriaMueble,
        on_delete= models.CASCADE,
        null=True
    )
    def __str__(self):
        return self.nombre

class comuna(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)
    def __str__(self):
        return self.descripcion

class tipoCuenta(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)
    def __str__(self):
        return self.descripcion

class cuenta(models.Model):
    id = models.AutoField(primary_key=True)
    usuario_cuenta =  models.IntegerField(default=0)
    nombre = models.CharField(max_length=70)
    direccion = models.CharField(max_length=70)
    correo = models.CharField(max_length=70)
    rut = models.CharField(max_length=9)
    telefono = models.CharField(max_length=9,null=True)
    comuna = models.ForeignKey(
        comuna,
        on_delete= models.CASCADE
    )
    def __str__(self):
        return self.nombre

class tipoEnvio(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=30)
    def __str__(self):
            return self.descripcion
class compra(models.Model):

    idCompra = models.AutoField(primary_key=True)

    idCliente = models.ForeignKey(
        cuenta,
        on_delete=models.CASCADE
    )

    total = models.IntegerField(default=0)

    fecha = models.DateTimeField(auto_now_add=True)

    completada = models.BooleanField(default=False)
    def __int__(self):
        return self.idCompra
    
class estadoProductoComprado(models.Model):
    idestadocompra = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=30)
    def __int__(self):
        return self.idestadocompra


class detalleCompra(models.Model):

    idDetalle = models.AutoField(primary_key=True)

    idCompra = models.ForeignKey(
        compra,
        on_delete=models.CASCADE,
        related_name='detalles'
    )

    idMueble = models.ForeignKey(
        mueble,
        on_delete=models.CASCADE
    )
    #
    idEsProdCom = models.ForeignKey(
        estadoProductoComprado,
        on_delete=models.CASCADE,
        null=True
    )
    #


    cantidad = models.IntegerField(default=1)

    subtotal = models.IntegerField(default=0)

    class Meta:
        unique_together = ('idCompra', 'idMueble')

class envio(models.Model):
    idEnvio = models.AutoField(primary_key=True)
    idCompra = models.ForeignKey(
        compra,
        on_delete= models.CASCADE
    )
    idMueble = models.ForeignKey(
        mueble,
        on_delete= models.CASCADE
    )
    idCliente = models.ForeignKey(
        cuenta,
        on_delete= models.CASCADE
    )
    idTipoEnvio = models.ForeignKey(
        tipoEnvio,
        on_delete= models.CASCADE
    )
    total = models.IntegerField()
    fecha = models.DateTimeField()
    def __str__(self):
            return self.idEnvio