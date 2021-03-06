// POV-Ray version 3.6/3.7 scenery file "p_sky01.pov"
// author: Friedrich A. Lohmueller, 2000. Update Dec-2009 / Jan-2011 /Nov-2013
// homepage: http://www.f-lohmueller.de

//----------------------------------------------------------------------------
#version 3.7; // 3.6;
global_settings{ assumed_gamma 1.0 }
#default{ finish{ ambient 0.1 diffuse 0.9 }}
//----------------------------------------------------------------------------

#include "colors.inc"
#include "textures.inc"
// camera ------------------------------------------------------------
#declare Camera_0 = camera{ angle 80 
                            right    x*image_width/image_height
                            location  <0.0 , .70 ,-0.8>
                            look_at   <0.0 , 0.7 , 0.0>}
camera{Camera_0}
// sun ---------------------------------------------------------------
light_source{<1500,2500,-2500> color rgb<1,1,1> }
// sky ---------------------------------------------------------------
sphere{ <0,0,0>,1 hollow    //keep attention: keep sun lower than sky
        texture{ pigment{ gradient <0,1,0>
                          color_map{[0.0 color White *0.8 ]
                                    [0.8 color rgb<0.1,0.25,0.75> ]
                                    [1.0 color rgb<0.1,0.25,0.75> ]}
                        }
                 #if (version = 3.7 )  finish {emission 1 diffuse 0}
                 #else                 finish { ambient 1 diffuse 0}
                 #end 
               }
       scale 10000}
//--------------------------------------------------------------------


// ground ------------------------------------------------------------
plane{ <0,1,0>, 0 
       texture{ pigment{color rgb<0.35,0.65,0.0>*0.7}
                normal {bumps 0.75 scale 0.015}
              } // end of texture
     } // end of plane
//--------------------------------------------------------------------------
//---------------------------- objects in scene ----------------------------
//--------------------------------------------------------------------------
