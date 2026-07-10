import { useState } from "react";

import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import AnswerSection from "./components/AnswerSection";
import Footer from "./components/Footer";


function App(){


const [answer,setAnswer] = useState("");

const [sources,setSources] = useState([]);



return (

<div className="
min-h-screen
bg-[#09090b]
relative
">





<Navbar/>


<Hero

setAnswer={setAnswer}

setSources={setSources}

/>



<AnswerSection

answer={answer}

sources={sources}

/>



<Footer/>


</div>

)

}


export default App;