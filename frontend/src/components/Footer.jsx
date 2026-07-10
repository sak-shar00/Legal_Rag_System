import { Scale } from "lucide-react";

const Footer = () => {
  return (
    <footer className="border-t border-white/10 mt-20">

      <div className="
      max-w-7xl 
      mx-auto 
      px-6 
      py-6 
      flex 
      flex-col 
      md:flex-row 
      justify-between 
      items-center
      gap-3
      ">

        <div className="flex items-center gap-3">

          <div className="
          p-2 
          rounded-lg 
          bg-gradient-to-r 
          from-blue-500 
          to-purple-600
          ">

            <Scale 
            size={18} 
            className="text-white"
            />

          </div>


          <div>
            <h3 className="
            text-white 
            font-semibold
            ">
              LexAI
            </h3>

            <p className="
            text-gray-500 
            text-sm
            ">
              AI Legal Research Assistant
            </p>
          </div>

        </div>



        <p className="
        text-gray-500 
        text-sm
        ">
          © 2026 LexAI. All rights reserved.
        </p>


      </div>

    </footer>
  );
};


export default Footer;
