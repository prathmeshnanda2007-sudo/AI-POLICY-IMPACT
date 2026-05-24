import React from "react";

export const Component = () => {
  return (
   <div className="absolute inset-0 z-0 bg-transparent w-full h-full pointer-events-none overflow-hidden">
     {/* Soft Yellow Glow */}
     <div
       className="absolute inset-0 z-0 pointer-events-none"
       style={{
         backgroundImage: `
           radial-gradient(circle at center, #FFF991 0%, transparent 70%)
         `,
         opacity: 0.15, // Adjusted from 0.6 to 0.15 so it works well behind the shader in dark mode
         mixBlendMode: "screen", // Changed from multiply to screen for dark mode compatibility
       }}
     />
     {/* Lime Center Glow */}
     <div 
       className="absolute inset-0 z-0 pointer-events-none" 
       style={{
         backgroundImage: `
           radial-gradient(circle at center, #84cc16, transparent)
         `,
         opacity: 0.2, // Added opacity to prevent overwhelming the dark theme
         mixBlendMode: "screen",
       }} 
     />
   </div>
  );
};

export default Component;
