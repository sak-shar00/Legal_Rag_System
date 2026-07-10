import { Sparkles, ShieldCheck } from "lucide-react";
import SourceCard from "./SourceCard";


const AnswerSection = ({
answer,
sources
})=>{


return (

<section className="
max-w-7xl
mx-auto
px-6
py-20
">


<div className="mb-10">


<div className="
flex
items-center
gap-2
text-blue-400
mb-3
">

<Sparkles size={20}/>

AI Generated Analysis

</div>



<h2 className="
text-3xl
font-bold
text-white
">

Research Result

</h2>


</div>




<div className="
bg-white/5
border
border-white/10
rounded-3xl
p-8
backdrop-blur-xl
">


<div className="
flex
items-center
gap-3
mb-6
">

<ShieldCheck
className="text-green-400"
/>


<span className="
text-green-400
text-sm
">

Verified from legal sources

</span>


</div>




<p className="
text-gray-300
leading-relaxed
text-lg
">


{
answer ||
"Ask a legal question to generate AI analysis."
}


</p>


</div>




<div className="mt-12">


<h3 className="
text-xl
font-semibold
text-white
mb-6
">

Source Citations

</h3>



<div className="
grid
md:grid-cols-2
gap-6
">


{
sources.map((source,index)=>(

<SourceCard

key={index}

source={source}

/>

))
}



</div>


</div>


</section>

)

}


export default AnswerSection;