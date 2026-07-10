import { Scale } from "lucide-react";
import { motion } from "framer-motion";


const Navbar = () => {
  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="
      w-full 
      border-b 
      border-white/10
      bg-black/20
      backdrop-blur-xl
      "
    >

      <div className="
      max-w-7xl 
      mx-auto 
      px-6 
      py-5
      flex 
      items-center 
      justify-between
      ">


        {/* Logo */}

        <div className="flex items-center gap-3">

          <div className="
          p-2 
          rounded-xl
          bg-gradient-to-br 
          from-blue-500 
          to-purple-600
          ">

            <Scale 
            size={24}
            className="text-white"
            />

          </div>


          <div>

            <h1 className="
            text-xl 
            font-semibold 
            text-white
            ">
              LexAI
            </h1>


            <p className="
            text-xs 
            text-gray-400
            ">
              Legal Research Assistant
            </p>

          </div>

        </div>



        {/* Right */}

        <div className="
        hidden md:flex
        items-center
        gap-6
        text-sm
        text-gray-400
        ">

          <span>
            Documents
          </span>

          <span>
            AI Search
          </span>

          <span>
            RAG Engine
          </span>


        </div>


      </div>

    </motion.nav>
  )
}


export default Navbar;