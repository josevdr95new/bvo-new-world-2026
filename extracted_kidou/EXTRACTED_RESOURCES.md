# Recursos extraídos de Bleach Kidou Wars 5.00

> Mapa descargado de: https://www.hiveworkshop.com/threads/bleach-kidou-wars-5-00.142486/
> Tamaño: 4.3 MB | Archivos extraídos: 274

## 🎯 Lo que se extrajo

### war3map.j (Script JASS completo — 67 KB)
¡El script JASS NO está protegido en este mapa! Se extrajo completo.

### Código de Gin Ichimaru encontrado:

#### Trigger: Shinso
- **Item ID**: `I013` (activa el Shikai al recogerlo)
- **Sound**: `gg_snd_Gin_Ichimarus_shikai___Shinsou`
- **Abilities**: `A02V` y `A02W` (se añaden al ZanCaster)
- **Mecánica**: Sistema compartido de Zanpakuto — al recoger el item I013,
  se crea un dummy projectile, se reproduce el sonido de Shinsou, y se
  otorgan las habilidades A02V + A02W al héroe

#### Trigger: Gintei
- Trigger separado llamado en `InitTrig_Gintei()`
- Probablemente maneja el movimiento o teleport de Gin

#### Código de acción extraído del war3map.j:
```jass
set udg_TempDummyProjectile = GetLastCreatedUnit()
call UnitApplyTimedLifeBJ( 3.00, 'BTLF', udg_TempDummyProjectile )
call PlaySoundAtPointBJ( gg_snd_Gin_Ichimarus_shikai___Shinsou, 100, udg_TempLoc1, 0 )
call UnitAddAbilityBJ( 'A02V', udg_ZanCaster )
call UnitAddAbilityBJ( 'A02W', udg_ZanCaster )
call GroupAddUnitSimple( udg_ZanCaster, udg_KyoukaEffectGroup )
call GroupAddUnitSimple( udg_ZanCaster, udg_FallGroup )
call CreateTextTagLocBJ( "TRIGSTR_1582", udg_TempLoc1, 0, 10, 100, 100, 100, 0 )
```

### Recursos del mapa
- **war3map.j**: 67,584 bytes (script JASS completo, NO protegido)
- **war3map.w3u**: datos de unidades (heroes)
- **war3map.w3a**: datos de habilidades (A02V, A02W)
- **war3map.w3h**: modificaciones de héroes
- **war3map.imp**: 8 modelos importados
- **274 archivos totales** extraídos (4.2 MB)

### Importaciones del mapa (war3map.imp):
```
war3mapImported\NewGroundEX.mdx
war3mapImported\NuclearExplosion.mdx
war3mapImported\Kudakero.mp3
war3mapImported\Yamamoto Shikai - Ryujin Jaka.mp3
war3mapImported\EverGreen Tree.mdx
war3mapImported\TornadoMissile.mdx
war3mapImported\ScrolRed.mdx
war3mapImported\Attak Aura.mdx
war3mapImported\textures\normal1.blp
```

## 📝 Cómo aplicar esto a BVO New World 2026

### Lo que falta para implementar Gin en nuestro mapa:

1. **El sonido de Shinso** (`Gin_Ichimarus_shikai___Shinsou`):
   - No está como archivo importado en Kidou Wars
   - Probablemente es un sound del WC3 base o fue eliminado
   - Alternativa: usar un sonido de espada de WC3 (`MetalHeavyChop1.wav`)

2. **Las habilidades A02V y A02W**:
   - Están definidas en el `war3map.w3a` del Kidou Wars
   - Se necesita descomprimir el w3a para extraer sus datos completos
   - IDs: A02V (Shinso extend), A02W (Shinso retract)

3. **El item I013**:
   - Activa el Shikai al ser recogido
   - Se puede crear en Object Editor como un power-up item

4. **El sistema Zanpakuto compartido**:
   - Kidou Wars usa un sistema donde TODOS los Shikais funcionan igual:
     recoger un item → activar habilidades
   - En BVO New World podemos hacerlo más simple: habilidad directa

### Aplicación al mapa BVO New World 2026:

Ya tenemos el script JASS de Gin en:
`custom_heroes/gin_ichimaru/scripts/gin_abilities.j`

El código de Kidou Wars nos da:
- Los IDs de habilidades exactos (A02V, A02W)
- El sistema de activación (item-based)
- El efecto visual (dummy projectile + sonido)
- El nombre del sonido original

Podemos combinar ambos enfoques:
- Usar el código de Kidou Wars como referencia para el efecto visual
- Usar nuestro script gin_abilities.j para las mecánicas completas
- Importar el sonido si lo encontramos, o usar un sonido WC3 similar
