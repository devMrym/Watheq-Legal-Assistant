import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { FileText, MessageCircle, Sparkles, Shield, BookOpen } from "lucide-react";

const HeroSection = () => {
  return (
    <section className="min-h-screen flex items-center justify-center bg-background px-6">
      <div className="container mx-auto max-w-3xl text-center py-32">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
        >
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.15 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/8 border border-primary/15 text-primary text-sm font-medium mb-10"
          >
            <Sparkles className="w-4 h-4" />
            مدعوم بالذكاء الاصطناعي
          </motion.div>

          {/* Headline */}
          <h1 className="font-heading text-4xl md:text-5xl lg:text-[3.25rem] font-bold text-foreground leading-[1.4] mb-6">
            مساعدك الذكي لفهم وتحليل
            <br />
            <span className="text-primary">الأنظمة والقوانين السعودية</span>
          </h1>

          {/* Tagline */}
          <p className="text-lg font-heading font-semibold text-foreground/70 mb-5">
            خلك واثق مع <span className="text-primary">واثق</span>
          </p>

          {/* Subheadline */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.35 }}
            className="text-base md:text-lg text-muted-foreground max-w-2xl mx-auto mb-12 leading-relaxed"
          >
            منصتك الذكية لمراجعة وتحليل المستندات القانونية والإجابة على استفساراتك المتعلقة بالأنظمة السعودية.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link
              to="/analyzer"
              className="flex items-center gap-3 px-8 py-3.5 rounded-xl bg-primary text-primary-foreground font-heading font-bold text-base shadow-sm hover:shadow-md hover:bg-primary/90 transition-all duration-200"
            >
              <FileText className="w-5 h-5" />
              ابدأ تحليل مستند
            </Link>
            <Link
              to="/chat"
              className="flex items-center gap-3 px-8 py-3.5 rounded-xl bg-secondary text-foreground font-heading font-bold text-base border border-border hover:bg-secondary/80 transition-all duration-200"
            >
              <MessageCircle className="w-5 h-5" />
              اسأل واثق
            </Link>
          </motion.div>
        </motion.div>

        {/* Feature Cards */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.7 }}
          className="mt-28 grid grid-cols-1 md:grid-cols-3 gap-5"
        >
          {[
            { icon: FileText, title: "تحليل المستندات", desc: "رفع وتحليل العقود والمستندات القانونية تلقائياً" },
            { icon: Shield, title: "فحص الامتثال", desc: "التحقق من توافق المستندات مع الأنظمة السعودية" },
            { icon: BookOpen, title: "مرجع قانوني", desc: "الوصول الفوري للأنظمة والمواد القانونية ذات الصلة" },
          ].map((feature, i) => (
            <motion.div
              key={i}
              whileHover={{ y: -3 }}
              className="p-6 rounded-2xl bg-card border border-border shadow-sm text-center hover:shadow-md transition-all duration-200"
            >
              <div className="w-11 h-11 rounded-xl bg-primary/8 flex items-center justify-center mx-auto mb-4">
                <feature.icon className="w-5 h-5 text-primary" />
              </div>
              <h3 className="font-heading font-bold text-foreground mb-2">{feature.title}</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">{feature.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default HeroSection;
