import { FileText } from "lucide-react";


const SourceCard = ({
source
})=>{


return (

<div className="
bg-white/5
border
border-white/10
rounded-2xl
p-6
backdrop-blur-xl
">


<div className="
flex
items-center
gap-4
">


<div className="
p-3
rounded-xl
bg-blue-500/20
">

<FileText
className="text-blue-400"
/>

</div>


<div>

<h4 className="
text-white
font-medium
">

{
source.file ||
source.title
}

</h4>


<p className="
text-gray-400
text-sm
">

Legal Document

</p>


</div>


</div>




<div className="
grid
grid-cols-2
gap-4
mt-6
">


<div className="
bg-black/30
rounded-xl
p-4
">

<p className="text-gray-400 text-sm">
Page
</p>


<p className="text-white mt-1">
{
source.page
}

</p>


</div>



<div className="
bg-black/30
rounded-xl
p-4
">


<p className="text-gray-400 text-sm">
Score
</p>


<p className="text-white mt-1">
{
source.score
}

</p>


</div>


</div>


</div>

)

}


export default SourceCard;