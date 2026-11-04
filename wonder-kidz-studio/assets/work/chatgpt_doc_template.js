const fs=require('fs');
const {Document,Packer,Paragraph,TextRun,ImageRun,HeadingLevel,AlignmentType,PageBreak,LevelFormat}=require('docx');
const pages=[[1,'its_snowing','It\'s snowing! Waddles at the window','URGENT — posts today 1 PM ET'],[15,'stockings','Stockings by the fireplace','Thu 8 PM ET'],[21,'hot_cocoa','Hot cocoa under the blanket','Sat 9 AM ET'],[3,'snowman','Building a snowman','Sun 1 PM ET'],[5,'sledding','Waddles sledding on his belly','Next week'],[10,'tree_sled','Pulling the tree home on the sled','Next week'],[12,'ornaments','Hanging ornaments on the tree','Next week'],[25,'christmas_cards','Making Christmas cards','Next week'],[30,'toy_train','Toy train around the tree','Next week'],[45,'christmas_morning','Christmas morning','Next week']];
const P=(t,o={})=>new Paragraph({spacing:{after:120},...o,children:[new TextRun({text:t,...(o.run||{})})]});
const B=t=>new Paragraph({numbering:{reference:'b',level:0},spacing:{after:60},children:[new TextRun(t)]});
const img=(f,w,h,type)=>new Paragraph({alignment:AlignmentType.CENTER,children:[new ImageRun({type,data:fs.readFileSync(f),transformation:{width:w,height:h}})]});
const kids=[
 new Paragraph({heading:HeadingLevel.TITLE,children:[new TextRun('Wonder Kidz Studio — Coloring Pages for ChatGPT')]}),
 P('Upload this whole file to ChatGPT. It contains the instructions, a color reference and 10 black-and-white pages to color.',{run:{italics:true}}),
 new Paragraph({heading:HeadingLevel.HEADING_1,children:[new TextRun('Instructions for ChatGPT')]}),
 P('You are coloring pages from a children\'s Christmas coloring book. For EACH of the 10 numbered pages below, generate one colored version of that exact page.'),
 new Paragraph({heading:HeadingLevel.HEADING_2,children:[new TextRun('The coloring prompt (use for every page)')]}),
 P('Color this exact coloring page as if a child finished it with bright, bold crayons and markers. Keep every black outline, shape, character and object exactly where it is — do not redraw, add, remove or move anything, and do not add any text. Fill every area fully with bright, saturated, cheerful Christmas colors: candy red, holly green, sunny yellow, sky blue, warm orange and pink. Strong contrast, no pale or pastel tones, no grey wash. Keep a white page background behind the scene where the page is blank. Soft crayon texture is fine, but colors must be vivid. Portrait format, same proportions as the original page.',{run:{bold:true}}),
 new Paragraph({heading:HeadingLevel.HEADING_2,children:[new TextRun('Character colors (keep the same on every page)')]}),
 B('Pip the bear: warm honey-brown fur, lighter tan muzzle and tummy, pink cheeks, red-and-white striped scarf.'),
 B('Juniper the bunny: cream/beige fur, pink inner ears and cheeks, bright green knit hat with green pompom, red-and-white scarf.'),
 B('Waddles the penguin: navy blue body, white face and tummy, orange beak and feet, red earmuffs.'),
 B('Match the look of the two finished examples in the color reference below.'),
 new Paragraph({heading:HeadingLevel.HEADING_2,children:[new TextRun('How to send the results back')]}),
 B('Work through the pages in order, starting with Page 1 (it is needed first).'),
 B('Put all 10 colored images into ONE Word document (.docx). Under each image write its label exactly as shown, e.g. "Page 01 – its_snowing".'),
 B('One image per page of the document, full size, high resolution.'),
 B('If you cannot do all 10 at once, do them in batches and keep the same labels.'),
 new Paragraph({heading:HeadingLevel.HEADING_2,children:[new TextRun('Color reference (already colored, for style)')]}),
 img('reference.jpg',620,411,'jpg'),
];
for(const [n,k,title,when] of pages){
 kids.push(new Paragraph({children:[new PageBreak()]}));
 kids.push(new Paragraph({heading:HeadingLevel.HEADING_1,children:[new TextRun(`Page ${String(n).padStart(2,'0')} – ${k}`)]}));
 kids.push(P(`${title} · ${when}`,{run:{italics:true,color:when.startsWith('URGENT')?'C62033':'555555'}}));
 kids.push(img(`p${String(n).padStart(2,'0')}_${k}.png`,500,589,'png'));
}
const doc=new Document({
 numbering:{config:[{reference:'b',levels:[{level:0,format:LevelFormat.BULLET,text:'•',alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:540,hanging:270}}}}]}]},
 styles:{default:{document:{run:{font:'Arial',size:22}},
  title:{run:{font:'Arial',size:40,bold:true,color:'1C4A33'},paragraph:{spacing:{before:0,after:160},keepNext:true}},
  heading1:{run:{font:'Arial',size:32,bold:true,color:'C62033'},paragraph:{spacing:{before:120,after:120},keepNext:true}},
  heading2:{run:{font:'Arial',size:26,bold:true,color:'1C4A33'},paragraph:{spacing:{before:240,after:100},keepNext:true}}}},
 sections:[{properties:{page:{size:{width:12240,height:15840},margin:{top:1080,bottom:1080,left:1080,right:1080}}},children:kids}]});
Packer.toBuffer(doc).then(b=>fs.writeFileSync('Wonder Kidz - ChatGPT coloring pages.docx',b));
