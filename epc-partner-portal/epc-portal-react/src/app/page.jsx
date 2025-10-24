import Image from 'next/image'
import Link from 'next/link'
import { Button } from '@/components/Button'
import { SaberLayout } from '@/components/SaberLayout'

import blurCyanImage from '@/images/blur-cyan.png'
import blurIndigoImage from '@/images/blur-indigo.png'

export default function HomePage() {
  return (
    <SaberLayout>
      <div className="overflow-hidden bg-slate-900">
      <div className="py-16 sm:px-2 lg:relative lg:px-0 lg:py-20">
        <div className="mx-auto grid max-w-2xl grid-cols-1 items-center gap-x-8 gap-y-16 px-4 lg:max-w-8xl lg:grid-cols-2 lg:px-8 xl:gap-x-16 xl:px-12">
          <div className="relative z-10 md:text-center lg:text-left">
            <Image
              className="absolute right-full bottom-full -mr-72 -mb-56 opacity-50"
              src={blurCyanImage}
              alt=""
              width={530}
              height={530}
              unoptimized
              priority
            />
            <div className="relative">
              <p className="inline bg-gradient-to-r from-green-200 via-sky-400 to-green-200 bg-clip-text font-display text-5xl tracking-tight text-transparent">
                Infinite Power In Partnership
              </p>
              <p className="mt-2 text-lg tracking-tight font-medium" style={{ color: '#7CC061' }}>
              Let’s Partner to Build the Future of Energy Together
              </p>
              <p className="mt-4 text-lg tracking-tight text-slate-400">
              Saber Renewable Energy is driving the transition to sustainable energy through innovative solutions, bespoke funding models like our Blended PPA, and a commitment to excellence. Our success is amplified by strong, collaborative partnerships. If you are a forward-thinking supplier, installer, developer, funder, consultant, or strategic introducer who shares our passion for quality and sustainability, we invite you to explore partnership opportunities with us.
              </p>
              <div className="mt-8 flex gap-4 md:justify-center lg:justify-start">
                <Button
                  href="/apply"
                  className="rounded-full py-2 px-4 text-sm font-semibold text-white transition-colors hover:opacity-90"
                  style={{ backgroundColor: '#7CC061' }}
                >
                  Submit Application
                </Button>
                <Button
                  href="https://saberrenewables.com/partnerships-in-actions/"
                  variant="secondary"
                  className="rounded-full bg-slate-800 py-2 px-4 text-sm font-medium text-white hover:bg-slate-700"
                >
                  Learn More
                </Button>
              </div>
            </div>
          </div>
          
          <div className="relative lg:static xl:pl-10">
            <div className="absolute inset-x-[-50vw] -top-32 -bottom-48 [mask-image:linear-gradient(transparent,white,white)] lg:-top-32 lg:right-0 lg:-bottom-32 lg:left-[calc(50%+14rem)] lg:[mask-image:none] dark:[mask-image:linear-gradient(transparent,white,transparent)] lg:dark:[mask-image:linear-gradient(white,white,transparent)]">
            </div>
            <div className="relative">
              <Image
                className="absolute -top-64 -right-64"
                src={blurCyanImage}
                alt=""
                width={530}
                height={530}
                unoptimized
                priority
              />
              <Image
                className="absolute -right-44 -bottom-40"
                src={blurIndigoImage}
                alt=""
                width={567}
                height={567}
                unoptimized
                priority
              />
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-tr from-green-300 via-green-300/70 to-blue-300 opacity-10 blur-lg" />
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-tr from-green-300 via-green-300/70 to-blue-300 opacity-10" />
              <div className="relative rounded-2xl bg-[#0A101F]/80 ring-1 ring-white/10 backdrop-blur-sm">
                <div className="absolute -top-px right-11 left-20 h-px bg-gradient-to-r from-green-300/0 via-green-300/70 to-green-300/0" />
                <div className="absolute right-20 -bottom-px left-11 h-px bg-gradient-to-r from-blue-400/0 via-blue-400 to-blue-400/0" />
                
                <div className="p-8">
                  <h3 className="text-xl font-semibold text-white mb-4">
                    Why Partner with Saber?
                  </h3>
                  
                  <div className="space-y-4 text-sm text-slate-300">
                    <div className="flex items-start gap-3">
                      <div className="h-2 w-2 rounded-full mt-2 flex-shrink-0" style={{ backgroundColor: '#7CC061' }} />
                      <div>
                        <div className="font-medium text-white">Access to Quality Projects</div>
                        <div>Engage with a growing pipeline of diverse renewable energy projects across various sectors throughout the UK, delivered with technical expertise and commercial focus.</div>
                        </div>
                    </div>
                    
                    <div className="flex items-start gap-3">
                      <div className="h-2 w-2 rounded-full mt-2 flex-shrink-0" style={{ backgroundColor: '#7CC061' }} />
                      <div>
                        <div className="font-medium text-white">Streamlined Collaboration</div>
                        <div>Benefit from our professional project management and clear communication processes, ensuring smooth and efficient collaboration.</div>
                      </div>
                    </div>
                    
                    <div className="flex items-start gap-3">
                      <div className="h-2 w-2 rounded-full mt-2 flex-shrink-0" style={{ backgroundColor: '#7CC061' }} />
                      <div>
                        <div className="font-medium text-white">Shared Growth & Opportunity</div>
                        <div>Be part of an ambitious company backed by reputable private equity, focused on scaling impactful, sustainable energy solutions.</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    </SaberLayout>
  )
}