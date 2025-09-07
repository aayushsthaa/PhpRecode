<?php
require_once 'config/config.php';

$pageTitle = 'Home';
include 'includes/header.php';
?>

<div class="container-fluid px-0">
    <div class="row">
        <!-- Main Content -->
        <div class="col-lg-9">
            <?php
            $sections = getHomepageSections();
            foreach ($sections as $section):
                $articles = getSectionArticles($section['id'], $section['max_articles']);
                if (empty($articles)) continue;
            ?>
            
            <section class="py-4 border-bottom">
                <div class="container">
                    <div class="row mb-4">
                        <div class="col">
                            <h2 class="section-title border-start border-danger border-4 ps-3 mb-0"><?php echo $section['name']; ?></h2>
                        </div>
                    </div>
                    
                    <?php if ($section['layout_type'] == 'featured'): ?>
                    <!-- Featured Layout -->
                    <div class="row">
                        <?php foreach ($articles as $index => $article): ?>
                        <?php if ($index == 0): ?>
                        <!-- Main Featured Article -->
                        <div class="col-lg-8">
                            <div class="featured-article">
                                <?php if ($article['featured_image']): ?>
                                <img src="/<?php echo $article['featured_image']; ?>" class="img-fluid rounded mb-3" alt="<?php echo htmlspecialchars($article['title']); ?>">
                                <?php endif; ?>
                                <h3><a href="/article.php?slug=<?php echo $article['slug']; ?>" class="text-decoration-none text-dark"><?php echo $article['title']; ?></a></h3>
                                <p class="text-muted mb-2">
                                    <small>By <?php echo $article['author_name']; ?> • <?php echo formatDate($article['published_at']); ?></small>
                                </p>
                                <p class="lead"><?php echo truncateText($article['excerpt'] ?: strip_tags($article['content']), 200); ?></p>
                            </div>
                        </div>
                        <div class="col-lg-4">
                        <?php else: ?>
                        <!-- Side Articles -->
                            <div class="side-article mb-3 pb-3 border-bottom">
                                <div class="row">
                                    <?php if ($article['featured_image']): ?>
                                    <div class="col-4">
                                        <img src="/<?php echo $article['featured_image']; ?>" class="img-fluid rounded" alt="<?php echo htmlspecialchars($article['title']); ?>">
                                    </div>
                                    <div class="col-8">
                                    <?php else: ?>
                                    <div class="col-12">
                                    <?php endif; ?>
                                        <h6><a href="/article.php?slug=<?php echo $article['slug']; ?>" class="text-decoration-none text-dark"><?php echo $article['title']; ?></a></h6>
                                        <p class="text-muted mb-0">
                                            <small><?php echo formatDate($article['published_at']); ?></small>
                                        </p>
                                    </div>
                                </div>
                            </div>
                        <?php endif; ?>
                        <?php endforeach; ?>
                        </div>
                    </div>
                    
                    <?php elseif ($section['layout_type'] == 'grid'): ?>
                    <!-- Grid Layout -->
                    <div class="row">
                        <?php foreach ($articles as $article): ?>
                        <div class="col-lg-4 col-md-6 mb-4">
                            <div class="card h-100 border-0 shadow-sm">
                                <?php if ($article['featured_image']): ?>
                                <img src="/<?php echo $article['featured_image']; ?>" class="card-img-top" alt="<?php echo htmlspecialchars($article['title']); ?>">
                                <?php endif; ?>
                                <div class="card-body">
                                    <h5 class="card-title">
                                        <a href="/article.php?slug=<?php echo $article['slug']; ?>" class="text-decoration-none text-dark"><?php echo $article['title']; ?></a>
                                    </h5>
                                    <p class="card-text text-muted"><?php echo truncateText($article['excerpt'] ?: strip_tags($article['content']), 120); ?></p>
                                    <div class="d-flex justify-content-between align-items-center">
                                        <small class="text-muted">By <?php echo $article['author_name']; ?></small>
                                        <small class="text-muted"><?php echo formatDate($article['published_at']); ?></small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <?php endforeach; ?>
                    </div>
                    
                    <?php else: ?>
                    <!-- List Layout -->
                    <div class="row">
                        <?php foreach ($articles as $article): ?>
                        <div class="col-12 mb-3">
                            <div class="row border-bottom pb-3">
                                <?php if ($article['featured_image']): ?>
                                <div class="col-md-3">
                                    <img src="/<?php echo $article['featured_image']; ?>" class="img-fluid rounded" alt="<?php echo htmlspecialchars($article['title']); ?>">
                                </div>
                                <div class="col-md-9">
                                <?php else: ?>
                                <div class="col-12">
                                <?php endif; ?>
                                    <h5><a href="/article.php?slug=<?php echo $article['slug']; ?>" class="text-decoration-none text-dark"><?php echo $article['title']; ?></a></h5>
                                    <p class="text-muted mb-2">
                                        <small>By <?php echo $article['author_name']; ?> • <?php echo formatDate($article['published_at']); ?></small>
                                    </p>
                                    <p class="mb-0"><?php echo truncateText($article['excerpt'] ?: strip_tags($article['content']), 150); ?></p>
                                </div>
                            </div>
                        </div>
                        <?php endforeach; ?>
                    </div>
                    <?php endif; ?>
                </div>
            </section>
            
            <?php endforeach; ?>
        </div>
        
        <!-- Sidebar -->
        <div class="col-lg-3">
            <div class="sidebar p-4 bg-light">
                <?php
                $widgets = getSidebarWidgets();
                foreach ($widgets as $widget):
                ?>
                
                <div class="widget mb-4">
                    <?php if ($widget['title']): ?>
                    <h5 class="widget-title border-bottom pb-2 mb-3"><?php echo $widget['title']; ?></h5>
                    <?php endif; ?>
                    
                    <?php if ($widget['widget_type'] == 'recent_articles'): ?>
                    <ul class="list-unstyled">
                        <?php
                        $recentArticles = getArticles(5, 0, 'published');
                        foreach ($recentArticles as $article):
                        ?>
                        <li class="mb-3">
                            <h6 class="mb-1">
                                <a href="/article.php?slug=<?php echo $article['slug']; ?>" class="text-decoration-none text-dark"><?php echo $article['title']; ?></a>
                            </h6>
                            <small class="text-muted"><?php echo formatDate($article['published_at']); ?></small>
                        </li>
                        <?php endforeach; ?>
                    </ul>
                    
                    <?php elseif ($widget['widget_type'] == 'categories'): ?>
                    <ul class="list-unstyled">
                        <?php
                        $categories = getCategories();
                        foreach ($categories as $category):
                        ?>
                        <li class="mb-2">
                            <a href="/category.php?slug=<?php echo $category['slug']; ?>" class="text-decoration-none"><?php echo $category['name']; ?></a>
                        </li>
                        <?php endforeach; ?>
                    </ul>
                    
                    <?php elseif ($widget['widget_type'] == 'newsletter'): ?>
                    <div class="newsletter-widget">
                        <?php echo $widget['content']; ?>
                        <form class="mt-3">
                            <div class="input-group">
                                <input type="email" class="form-control" placeholder="Your email">
                                <button class="btn btn-primary" type="submit">Subscribe</button>
                            </div>
                        </form>
                    </div>
                    
                    <?php elseif ($widget['widget_type'] == 'custom_html'): ?>
                    <?php echo $widget['content']; ?>
                    
                    <?php endif; ?>
                </div>
                
                <?php endforeach; ?>
            </div>
        </div>
    </div>
</div>

<?php include 'includes/footer.php'; ?>
