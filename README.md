## Test ModbusRTU DDS238-2 

Para la realizacion de la intgeracion se utilizo la libreria PyModbus en entorno controlado, adicionalmente se realiza un compendio de los registros presentes para este dispositivo en ModbusRTU, a continuacion se desglosa el paso a paso realizado.

#### Indice
> I. Registros ModbusRTU HIKING-DDS238-2

> II. Test con PyModbus

----
##### I. Registos ModbusRTU HIKING-DDS238-2

![](https://raw.githubusercontent.com/23ft/HIKING-DDS238-2/main/hiking_register_map_rtu.PNG?token=GHSAT0AAAAAACOAP7J6QKGAPCHC2QMAJFGUZOGKBXQ)

Nota importante a la hora de escribir registros: The meter does not understand the 'write sigle register' function code (06h), only the 'write multiple registers' function code (10h).

----
##### II. Test con PyModbus

Se realiza integracion con la libreria PYMODBUS La cual presento comportamientos extraños en la lectura del registro 000Fh ya que al tender al valores negativos este registro retorna lo que parece ser un registro complemento a dos.

Validacion por registros de funcionamiento RELE y extraccion de informacion como lo es Export Energy, Voltaje, Active power, Power Factor etc.

