El usuario administrador de inventario crea un inventario borrador donde agrega
los productos a inventariar y los usuarios que participaran del inventario.

Cuando esta todo cargado, pasa el inventario de Borrador a En Proceso con el
boton iniciar inventario.

En ese momento se envian notificaciones a todos los participantes indicando que
tienen un inventario que hacer.

Cada participante abre su pagina y se le indica hacer un inventario de un grupo
de productos, el sistema se encarga de seleccionar los productos de manera que
no haya dos participantes que tengan el mismo producto.

Cuando el participante carga la cantidad de un producto esta linea del inventario
se vuelve grisada y no puede ser editada. El sistema toma fecha hora de ingreso
de cada linea de inventario por separado.

Cuando no quedan lineas por ingresar se envia una notificacion al administrador
indicando que el usuario tal, termino su inventario numero xx de un total de yy
y al refrescar la pagian el sistema le presenta otro conjunto de productos a
inventariar.

Cuando todos los participantes agotaron todos los inventarios pendientes, al
administrador de inventario le llega una notificacion de que el inventario esta
concluido y en el formulario de inventario se le habilita otra oreja con la
informacion recolectada.

La informacion se presenta como un grilla con filas representando productos y
columnas representando participantes en cada celda esta la cantidad ingresada
por el participante mas un ajuste.

El ajuste se hace tomando los ingresos y egresos de producto desde la fecha y
hora en la que el participante ingreso la cantidad de este producto hasta el
momento en que se visualiza la planilla. Esto puede resultar en que la
visualizacion sea un poco lenta.
