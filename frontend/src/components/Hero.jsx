import { motion } from "framer-motion";
import { FileText, Sparkles } from "lucide-react";

import SearchSection from "./SearchSection";


const Hero = ({
  setAnswer,
  setSources
}) => {


  return (

    <section className="
    relative
    min-h-[calc(100vh-90px)]
    flex
    items-center
    overflow-hidden
    ">


      {/* Background Glow */}

      <div className="
      absolute
      top-20
      left-1/2
      -translate-x-1/2
      w-[500px]
      h-[500px]
      bg-blue-600/20
      blur-[120px]
      rounded-full
      " />



      <div className="
      max-w-7xl
      mx-auto
      px-6
      py-20
      grid
      lg:grid-cols-2
      gap-16
      items-center
      relative
      z-10
      ">



        {/* Left Content */}


        <motion.div

        initial={{
          opacity:0,
          x:-40
        }}

        animate={{
          opacity:1,
          x:0
        }}

        transition={{
          duration:0.7
        }}

        >



          <div className="
          inline-flex
          items-center
          gap-2
          px-4
          py-2
          rounded-full
          bg-white/5
          border
          border-white/10
          text-sm
          text-gray-300
          mb-6
          ">


            <Sparkles
            size={16}
            className="text-blue-400"
            />


            Powered by RAG + AI


          </div>




          <h1 className="
          text-5xl
          lg:text-6xl
          font-bold
          leading-tight
          text-white
          ">


            Understand Legal
            Documents


            <span className="
            block
            bg-gradient-to-r
            from-blue-400
            to-purple-500
            bg-clip-text
            text-transparent
            ">

              With AI Precision

            </span>


          </h1>




          <p className="
          mt-6
          text-lg
          text-gray-400
          max-w-xl
          leading-relaxed
          ">


            Search through court judgments,
            tax regulations and legal documents
            using an intelligent AI research assistant.


          </p>




          {/* Dynamic Search Component */}


          <div className="mt-10">

            <SearchSection

            setAnswer={setAnswer}

            setSources={setSources}

            />


          </div>




        </motion.div>







        {/* Right Side Analytics Card */}



        <motion.div


        initial={{
          opacity:0,
          scale:0.8
        }}


        animate={{
          opacity:1,
          scale:1
        }}


        transition={{
          duration:0.8
        }}


        className="
        relative
        "


        >




          <div className="
          absolute
          -top-10
          -right-10
          w-72
          h-72
          bg-purple-600/20
          blur-3xl
          rounded-full
          " />





          <div className="
          relative
          bg-white/5
          border
          border-white/10
          backdrop-blur-xl
          rounded-3xl
          p-8
          shadow-2xl
          ">




            <div className="
            flex
            items-center
            gap-4
            mb-8
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


                <h3 className="
                text-white
                font-semibold
                ">

                  Legal Documents

                </h3>



                <p className="
                text-gray-400
                text-sm
                ">

                  100+ indexed files

                </p>



              </div>



            </div>







            <div className="
            grid
            grid-cols-2
            gap-4
            ">




              <div className="
              rounded-2xl
              bg-black/30
              p-5
              ">


                <p className="
                text-gray-400
                text-sm
                ">

                  Documents

                </p>



                <h2 className="
                text-3xl
                text-white
                font-bold
                mt-2
                ">

                  100+

                </h2>



              </div>







              <div className="
              rounded-2xl
              bg-black/30
              p-5
              ">


                <p className="
                text-gray-400
                text-sm
                ">

                  Accuracy

                </p>



                <h2 className="
                text-3xl
                text-white
                font-bold
                mt-2
                ">

                  91%

                </h2>



              </div>



            </div>




          </div>





        </motion.div>





      </div>



    </section>

  )

}



export default Hero;