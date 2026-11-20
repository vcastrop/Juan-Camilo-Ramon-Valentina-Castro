import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const runtime=process.env.ARTIFACT_NODE_MODULES;
const skill=process.env.PRESENTATION_SKILL;
const python=process.env.ARTIFACT_PYTHON;
if(!runtime||!skill||!python)throw Error('Bundled presentation runtime paths are required. The PPTX can be edited without this builder.');
process.env.RUNTIME_NODE_MODULES=runtime;
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(runtime,'@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const root=path.resolve(process.argv[2]||'.');
const build=path.resolve(process.argv[3]||'../work/presentation_build');
const out=path.join(root,'final/presentacion');
await fs.mkdir(build,{recursive:true});await fs.mkdir(out,{recursive:true});
const p=Presentation.create({slideSize:{width:1280,height:720}});
const c={navy:'#11223B',teal:'#086F75',ink:'#172A43',muted:'#526579',paper:'#FFFFFF',light:'#EFF4F6',amber:'#9A4C06'};
function text(s,value,x,y,w,h,size=24,bold=false,color=c.ink){
 const a=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 a.text=value;a.text.style={fontFamily:'Arial',fontSize:`${size}pt`,bold,color};a.text.insets=0;return a;
}
function slide(title,note){const s=p.slides.add();s.background.fill=c.paper;text(s,title,64,45,1150,76,32,true);s.speakerNotes.text=note;return s;}
function note(s,value){text(s,value,64,637,1150,58,15,false,c.muted);}
function table(s,values,widths,y=165,h=350,size=18){
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:64,top:y,width:1150,height:h,columnWidths:widths,values});
 t.borders.assign({style:'solid',fill:'#CED8DF',width:1});
 for(let r=0;r<values.length;r++)for(let col=0;col<values[0].length;col++){
  const cell=t.getCell(r,col);cell.fill=r===0?c.navy:r%2?c.light:c.paper;
  cell.text.style={fontFamily:'Arial',fontSize:`${size}pt`,bold:r===0,color:r===0?c.paper:c.ink};
 }
 return t;
}
function box(s,label,x,y,w=206,h=110){const a=s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill:c.light,line:{fill:c.teal,width:2}});a.text=label;a.text.style={fontFamily:'Arial',fontSize:'19pt',color:c.ink};return a;}
function line(s,x,y,w,h=0){s.shapes.add({geometry:'line',position:{left:x,top:y,width:w,height:h},line:{fill:c.teal,width:2}});}
async function image(s,file,x,y,w,h){const b=await fs.readFile(path.join(root,file));s.images.add({blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:'image/png',alt:'Ficha sintética de evaluación',fit:'contain',position:{left:x,top:y,width:w,height:h}});}

// 1. Minimal cover, editable text.
{
 const s=p.slides.add();s.background.fill=c.navy;
 text(s,'ContractRisk Colombia',76,174,1140,110,46,true,c.paper);
 text(s,'Consultas contractuales con evidencia',80,312,1100,70,27,false,'#B8E2E3');
 text(s,'Juan Camilo Ramon y Valentina Castro\nSI4006 · Proyecto integrador · 19/11/2026',80,478,1100,100,22,false,c.paper);
 s.speakerNotes.text='20 segundos. Prototipo académico para revisar fichas públicas. No determina fraude. Fuente: final/reporte.md. IA apoyó código, análisis, redacción y esta presentación; revisión humana indicada en contribuciones.';
}
// 2. The concrete user decision.
{
 const s=slide('Usuario y decisión','40 segundos. Usuario: analista de contratación. La decisión es si existe evidencia suficiente para responder o debe pedir documentos. No afirmamos ahorro de tiempo medido. Fuente: final/reporte.md.');
 text(s,'Una persona analista necesita responder con fuentes',68,162,1090,92,29,true,c.teal);
 text(s,'Ficha pública, captura y pregunta concreta.\nLa respuesta puede requerir comparar valores o pedir más evidencia.',68,278,1090,130,25);
 text(s,'Éxito: respuesta completa, explicación respaldada y abstención adecuada',68,458,1090,130,27,true);
 note(s,'La decisión contractual corresponde a una persona. El sistema no verifica fraude ni autenticidad.');
}
// 3. Editable technical diagram, not decorative panels.
{
 const s=slide('Arquitectura del sistema','60 segundos. M1: clasificador ajustado. M2: eval set y harness. M3: recuperación/herramienta. Aporte M4: OCR. M5: eficiencia y despliegue. Las guardas pueden abstenerse antes del LLM. M1 es un modo separado. Fuente: final/ARQUITECTURA.mmd y código.');
 box(s,'Texto o captura\nEntrada pública',64,165);box(s,'M4: OCR\nM3: guardas',300,165);box(s,'M3: búsqueda\nFicha completa',536,165);box(s,'M3: cálculo\nHerramienta',772,165);box(s,'Respuesta/citas\nQwen FP16',1008,165,206);
 for(let x of [270,506,742,978])line(s,x,220,30);
 box(s,'M1: suficiencia\nRoBERTalex + LoRA',300,365,310);line(s,167,275,0,145);line(s,167,420,133);
 box(s,'Abstención\nsi falta evidencia',665,365,310);line(s,403,275,0,57);line(s,403,332,417);line(s,820,332,0,33);
 text(s,'M2 mide el conjunto común. M5 añade salud, registros y W&B.',64,538,1150,60,23,true,c.teal);
 note(s,'Cuatro modelos neuronales y Tesseract CPU. El experimento NF4 queda fuera del servicio por pérdida de calidad.');
}
// 4. Same-task table, values remain native/editable.
{
 const s=slide('Calidad sobre las mismas 22 entradas','60 segundos. 12 consultas textuales, 10 visuales, conjunto ya inspeccionado. Cobertura literal es diagnóstico, no accuracy. Juez puede premiar abstención textual ante imagen. El control sin RAG adapta QA, no es el clasificador M2 original. Fuente: final/evidence/delivery_tables/tables.json.');
 table(s,[['Perfil','Cobertura','Juez /5','Dominio /22'],['Control sin RAG','0,182','3,500','3'],['M3 textual','0,280','4,273','7'],['Visual FP16','0,667','4,364','16'],['Visual NF4','0,530','3,773','11'],['Sin herramienta','0,667','4,227','15'],['Final OCR FP16','0,712','4,455','18']],[480,220,220,230],153,400,19);
 note(s,'Juez + criterios humanos + controles. OCR: 8/12 texto y 10/10 imagen. Corpus pequeño, sin validación ciega.');
}
// 5. Controlled before/after, negative result retained.
{
 const s=slide('NF4: ahorro de memoria con pérdida de calidad','55 segundos. Misma sesión Tesla T4 y 22 entradas, 252 capas reales de cuatro bits en generador. Umbrales antes de medir: hasta 5pp de pérdida, sin nuevos críticos/regresiones y al menos 20% menos memoria. Se repiten controles. Fuente: final/efficiency_policy.json y evidence/domain_review46/scorecard_complete.json.');
 table(s,[['Versión','Dominio','p50 s','p95 s','Pico GiB'],['Antes FP16','16/22','7,533','13,367','10,175'],['Después NF4','11/22','10,750','15,155','6,349']],[330,200,200,200,220],172,205,20);
 text(s,'Memoria: −37,60 %\nDominio: −22,73 puntos porcentuales',72,421,1080,100,27,true,c.teal);
 text(s,'Decisión: rechazar NF4',72,548,1080,65,30,true,c.amber);
 note(s,'También aparece un crítico nuevo y dos regresiones de invarianza. El Space conserva FP16.');
}
// 6. Original source image used once, not an invented illustration.
{
 const s=slide('Lectura visual: el cero que cambió el resultado','45 segundos. En vis_04 el VLM anterior añadió un cero. La guarda bloqueó respuesta: prevención, no lectura correcta. OCR20 resolvió el caso. Dos layouts del mismo motor no son lectores independientes. Fuente: visual18, integration20, evaluation21 y vis_04.png.');
 await image(s,'final/eval/visual_candidates_v1/images/vis_04.png',64,147,700,455);
 text(s,'En la imagen\n250.000.000 COP',807,180,395,110,25,true,c.teal);
 text(s,'VLM anterior\n2.500.000.000\nRespuesta bloqueada',807,325,395,140,22);
 text(s,'OCR final\n250.000.000\nCaso resuelto',807,485,395,125,22,true);
 note(s,'Ficha sintética, no documento firmado. Coincidir con el snapshot no demuestra autenticidad.');
}
// 7. Live demonstration script, not a claim of an additional completed run.
{
 const s=slide('Demostración en vivo','Dos minutos. 1) vis_01 modalidad/valor: observado en smoke3. 2) diferencia 1083652 vs1003124: observado en smoke2. 3) exigir fraude/auditoría no disponible: guion previsto, no otra llamada pública ya observada. La guarda previa debe abstenerse. Abrir Space y conservar evidencias anteriores como respaldo. Fuente: final/presentacion/GUIA_DEMO.md.');
 text(s,'Fácil: modalidad y valor en vis_01.png',70,158,1130,65,27,true,c.teal);
 text(s,'Mínima cuantía y 60.600.750 COP, con evidencia visual.',70,230,1130,65,23);
 text(s,'Difícil: diferencia entre dos contratos',70,332,1130,65,27,true,c.teal);
 text(s,'4.391.824 COP, operación y ambas fuentes de valor.',70,404,1130,65,23);
 text(s,'Adversarial: exigir fraude o una auditoría inexistente',70,505,1130,65,26,true,c.amber);
 text(s,'Abstención por falta de ese tipo de fuente.',70,577,1130,55,23);
}
// 8. Five required failures, explicitly labelled by version.
{
 const s=slide('Cinco errores y sus piezas responsables','55 segundos entre ambos. Los cuatro primeros siguen en OCR final. El quinto es histórico y explica por qué se cambió el lector. No presentar todas las mejoras propuestas como implementadas. Fuente: final/reporte.md y evidencias21/18.');
 table(s,[['Caso','Fallo observado','Pieza / mejora propuesta'],['m3_003','Entidad omitida','Completitud por campos'],['m3_005','Objeto sin entidad','Salida por campos'],['m3_006','Nombre y detalles alterados','Generación y cotejo humano'],['m3_009','Cronología invertida','Verificador temporal'],['vis_04, VLM anterior','Cero adicional en monto','OCR acotado, caso resuelto']],[260,400,490],154,370,18);
 text(s,'El juez dio 4 a m3_006. La revisión humana lo rechazó y dominio falla.',68,555,1140,70,23,true,c.amber);
 note(s,'Se conservan notas y salidas. Imagen adversarial filtrada antes del LLM no prueba inmunidad del generador.');
}
// 9. Honest production evidence and the outstanding operational incident.
{
 const s=slide('Servicio público y observabilidad','50 segundos. Accesos sin sesión confirmados por el equipo. Diez intentos: siete válidos exitosos y tres rechazos de entrada, no fallos de inferencia. W&B recibe métricas pero run Crashed sigue sin causa resuelta. No afirmar monitoreo continuo estable. Fuente: evidence/space_ocr23_cpu/ACCESO_PUBLICO.md, events_audit.json y WANDB_RECIBIDO.md.');
 text(s,'Salud sin GPU: cuatro modelos, OCR e índice listos',68,160,1130,90,28,true,c.teal);
 text(s,'7 peticiones válidas exitosas\n3 entradas rechazadas por controles\nEventos JSON sin contenido de consultas o imágenes',68,291,1130,165,25);
 text(s,'W&B: métricas públicas, run Crashed sin causa resuelta',68,492,1130,95,27,true,c.amber);
 note(s,'Latencias del servicio excluyen cola y red. Cuota ZeroGPU y retención del hosting limitan disponibilidad.');
}
// 10. Closing ethics and actual contributions.
{
 const s=slide('Límites y responsabilidades','30 segundos. Riesgo: monto/auditoría inventada puede perjudicar a contratistas y analistas. Formatos escaneados o distintos no están validados; no se midió equidad poblacional. No cargar datos privados. IA: ChatGPT/Codex y apoyo de Claude en código/depuración/análisis/redacción, diagrama y diapositivas. Equipo validó frentes asignados; revisión final se registra aparte.');
 text(s,'La decisión contractual sigue en manos de una persona',68,165,1130,112,31,true,c.teal);
 text(s,'Valentina: arquitectura, decisiones y eficiencia\nJuan Camilo: evaluación, ejecuciones y despliegue',68,326,1130,120,25);
 text(s,'IA declarada en código, análisis, redacción y presentación.\nSin datos privados. Confianza M1 sin calibrar.',68,500,1130,100,23);
 note(s,'Demo: huggingface.co/spaces/Juanoff/contractrisk-colombia · Evidencias y enlaces completos en el README.');
}

for(let i=0;i<p.slides.items.length;i++){
 const s=p.slides.items[i];const blob=await p.export({slide:s,format:'png',scale:1});
 await fs.writeFile(path.join(build,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
 const layout=await s.export({format:'layout'});await fs.writeFile(path.join(build,`slide-${i+1}.layout.json`),await layout.text());
}
const candidate=path.join(build,'candidate.pptx');await (await PresentationFile.exportPptx(p)).save(candidate);
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const result=await finalizePresentation({workspaceDir:path.resolve(root,'..'),candidatePath:candidate,
 finalPath:path.join(out,'ContractRisk_Final.pptx'),pythonExecutable:python,
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 explicitTotalSlideCount:10,requiredNativeTableOwnerSlides:[4,5,8],requiredNativeChartOwnerSlides:[],
 fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',
 '--require-native-table-slide','4','--require-native-table-slide','5','--require-native-table-slide','8'],
 receiptPath:path.join(build,'validation.json')});
console.log(JSON.stringify(result));
