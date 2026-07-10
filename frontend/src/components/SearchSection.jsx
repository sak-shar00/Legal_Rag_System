import { useState } from "react";
import { Search } from "lucide-react";

import { askLegalQuestion } from "../services/api";


const SearchSection = ({
  setAnswer,
  setSources
}) => {


  const [question, setQuestion] = useState("");

  const [loading, setLoading] = useState(false);



  const handleSearch = async () => {


    if (!question.trim()) return;


    try {


      setLoading(true);


      const res = await askLegalQuestion(question);



      const rawAnswer = res.data.answer || "";


const cleanAnswer = rawAnswer
  .replace(/-{5,}/g, "")
  .replace(/^\s*Answer\s*/i, "")
  .replace(/\([^)]*\.pdf[^)]*\)/g, "")
  .split("Primary Citation")[0]
  .split("Additional References")[0]
  .trim();



      setAnswer(cleanAnswer);



      setSources(res.data.sources || []);



    } catch (error) {


      console.log(error);


      setAnswer("Unable to fetch legal answer.");

      setSources([]);


    } finally {


      setLoading(false);


    }


  };




  return (

    <div className="
    flex
    items-center
    gap-3
    bg-white/5
    border
    border-white/10
    rounded-2xl
    p-3
    backdrop-blur-xl
    max-w-xl
    ">


      <Search
        size={22}
        className="text-gray-400 ml-3"
      />



      <input

        value={question}

        onChange={(e)=>setQuestion(e.target.value)}

        placeholder="Ask a legal question..."

        className="
        flex-1
        bg-transparent
        outline-none
        text-white
        placeholder:text-gray-500
        "

      />



      <button

        onClick={handleSearch}

        className="
        px-5
        py-3
        rounded-xl
        bg-gradient-to-r
        from-blue-500
        to-purple-600
        text-white
        font-medium
        "

      >

        {
          loading
          ?
          "Searching..."
          :
          "Search"
        }


      </button>



    </div>

  )

}


export default SearchSection;