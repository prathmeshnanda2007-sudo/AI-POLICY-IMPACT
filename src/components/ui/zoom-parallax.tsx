'use client';

import { useScroll, useTransform, motion } from 'framer-motion';
import { useRef } from 'react';

interface Image {
	src: string;
	alt?: string;
}

interface ZoomParallaxProps {
	/** Array of images to be displayed in the parallax effect max 7 images */
	images: Image[];
}

export function ZoomParallax({ images }: ZoomParallaxProps) {
	const container = useRef(null);
	const { scrollYProgress } = useScroll({
		target: container,
		offset: ['start start', 'end end'],
	});

	const scale4 = useTransform(scrollYProgress, [0, 1], [1, 4]);
	const scale5 = useTransform(scrollYProgress, [0, 1], [1, 5]);
	const scale6 = useTransform(scrollYProgress, [0, 1], [1, 6]);
	const scale8 = useTransform(scrollYProgress, [0, 1], [1, 8]);
	const scale9 = useTransform(scrollYProgress, [0, 1], [1, 9]);

	const scales = [scale4, scale5, scale6, scale5, scale6, scale8, scale9];

	const getPositionClasses = (index: number) => {
		switch (index) {
			case 0: return 'h-[30vh] w-[70vw] md:h-[25vh] md:w-[25vw]'; // Center
			case 1: return '-top-[25vh] left-[5vw] h-[20vh] w-[45vw] md:-top-[30vh] md:h-[30vh] md:w-[35vw]';
			case 2: return '-top-[15vh] -left-[20vw] h-[25vh] w-[35vw] md:-top-[10vh] md:-left-[25vw] md:h-[45vh] md:w-[20vw]';
			case 3: return 'left-[20vw] h-[20vh] w-[40vw] md:left-[27.5vw] md:h-[25vh] md:w-[25vw]';
			case 4: return 'top-[25vh] left-[5vw] h-[20vh] w-[40vw] md:top-[27.5vh] md:h-[25vh] md:w-[20vw]';
			case 5: return 'top-[20vh] -left-[20vw] h-[20vh] w-[45vw] md:top-[27.5vh] md:-left-[22.5vw] md:h-[25vh] md:w-[30vw]';
			case 6: return 'top-[22.5vh] left-[20vw] h-[15vh] w-[30vw] md:left-[25vw] md:h-[15vh] md:w-[15vw]';
			default: return 'h-[25vh] w-[25vw]';
		}
	};

	return (
		<div ref={container} className="relative h-[300vh]">
			<div className="sticky top-0 h-screen overflow-hidden">
				{images.map(({ src, alt }, index) => {
					const scale = scales[index % scales.length];

					return (
						<motion.div
							key={index}
							style={{ scale }}
							className="absolute top-0 flex h-full w-full items-center justify-center"
						>
							<div className={`relative shadow-2xl rounded-2xl overflow-hidden border border-slate-200 ${getPositionClasses(index)}`}>
								<img
									src={src || '/placeholder.svg'}
									alt={alt || `Parallax image ${index + 1}`}
									className="h-full w-full object-cover"
								/>
							</div>
						</motion.div>
					);
				})}
			</div>
		</div>
	);
}
